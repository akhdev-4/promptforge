"""Personalized "For You" recommendation feed.

Builds a per-user feed from the prompts they've bookmarked: each bookmark is a
"seed" fed to the heuristic related-provider, and the resulting candidates are
scored by rank across every seed (a prompt surfaced by many bookmarks, high up,
wins). We exclude the user's own prompts and the seeds themselves, then top up
with trending prompts so new users (no bookmarks) still get a useful feed.

The provider is pluggable (see app.recommendations), so swapping the heuristic
for an embedding/vector model later needs no change here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromptStatus
from app.models.prompt import Prompt
from app.recommendations import get_related_provider
from app.repositories.prompt import PromptRepository
from app.services.interaction import InteractionService

# How many recent bookmarks to seed from, and how many candidates to pull per
# seed. Kept small so the feed is cheap to assemble.
_MAX_SEEDS = 8
_PER_SEED = 20


@dataclass
class Recommendation:
    prompt: Prompt
    reason: str


class RecommendationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompts = PromptRepository(session)
        self.interactions = InteractionService(session)
        self.provider = get_related_provider()

    async def for_user(self, user_id: uuid.UUID, *, limit: int = 12) -> list[Recommendation]:
        seeds, _ = await self.interactions.list_bookmarks(user_id, offset=0, limit=_MAX_SEEDS)
        seed_ids = {s.id for s in seeds}

        scores: dict[uuid.UUID, float] = {}
        prompts_by_id: dict[uuid.UUID, Prompt] = {}
        # Per candidate, the single strongest seed contribution → the "reason".
        best_seed: dict[uuid.UUID, tuple[float, str]] = {}

        for seed in seeds:
            related = await self.provider.related(self.session, seed, limit=_PER_SEED)
            for rank, cand in enumerate(related):
                # Skip only what they've already bookmarked — recommending a
                # user's own proven prompts back to them is fine on a sharing
                # platform (and keeps single-author demos from looking empty).
                if cand.id in seed_ids:
                    continue
                weight = float(_PER_SEED - rank)  # higher rank → higher weight
                scores[cand.id] = scores.get(cand.id, 0.0) + weight
                prompts_by_id[cand.id] = cand
                if cand.id not in best_seed or weight > best_seed[cand.id][0]:
                    best_seed[cand.id] = (weight, seed.title)

        ranked = sorted(scores, key=lambda cid: scores[cid], reverse=True)
        recs = [
            Recommendation(
                prompt=prompts_by_id[cid],
                reason=f'Because you bookmarked "{best_seed[cid][1]}"',
            )
            for cid in ranked[:limit]
        ]

        # Top up (or, for new users, fully populate) with trending prompts.
        if len(recs) < limit:
            seen = {r.prompt.id for r in recs} | seed_ids
            trending, _ = await self.prompts.search(
                offset=0,
                limit=limit + len(seen),
                status=PromptStatus.PUBLISHED,
                sort="most_copied",
            )
            for p in trending:
                if len(recs) >= limit:
                    break
                if p.id in seen:
                    continue
                recs.append(Recommendation(prompt=p, reason="Popular right now"))
                seen.add(p.id)

        return recs
