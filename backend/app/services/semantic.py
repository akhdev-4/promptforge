"""Semantic (embedding-based) prompt search.

Stores one Gemini embedding per prompt and ranks by cosine similarity to the
query embedding. Everything degrades gracefully: with no key / no embeddings,
``search`` returns None so the caller falls back to keyword search.
"""

from __future__ import annotations

import json
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding import PromptEmbedding
from app.models.enums import PromptStatus
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository
from app.search.embeddings import EMBED_MODEL, embed_text


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def _prompt_text(prompt: Prompt) -> str:
    tags = " ".join(t.slug for t in prompt.tags)
    return f"{prompt.title}\n{prompt.description or ''}\n{tags}\n{prompt.content[:1000]}"


class SemanticSearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embeds = BaseRepository(PromptEmbedding, session)

    async def reembed(self, prompt: Prompt) -> bool:
        """Compute + store a prompt's embedding. Best-effort (False if skipped)."""
        vector = await embed_text(_prompt_text(prompt))
        if vector is None:
            return False
        payload = json.dumps(vector)
        existing = await self.embeds.get_by(prompt_id=prompt.id)
        if existing:
            existing.vector = payload
            existing.model = EMBED_MODEL
            self.session.add(existing)
        else:
            await self.embeds.create(prompt_id=prompt.id, vector=payload, model=EMBED_MODEL)
        return True

    async def search(self, query: str, *, limit: int) -> list[Prompt] | None:
        query_vec = await embed_text(query)
        if query_vec is None:
            return None
        rows = list((await self.session.execute(select(PromptEmbedding))).scalars().all())
        if not rows:
            return None

        scored: list[tuple[float, uuid.UUID]] = []
        for row in rows:
            scored.append((_cosine(query_vec, json.loads(row.vector)), row.prompt_id))
        scored.sort(key=lambda s: s[0], reverse=True)
        top_ids = [pid for _, pid in scored[:limit]]
        if not top_ids:
            return []

        prompts = list(
            (
                await self.session.execute(
                    select(Prompt).where(
                        Prompt.id.in_(top_ids), Prompt.status == PromptStatus.PUBLISHED
                    )
                )
            )
            .unique()
            .scalars()
            .all()
        )
        by_id = {p.id: p for p in prompts}
        return [by_id[pid] for pid in top_ids if pid in by_id]

    async def backfill(self, *, batch: int = 20) -> tuple[int, int]:
        """Embed up to `batch` published prompts that don't have one yet.

        Returns (embedded_now, remaining) — call repeatedly until remaining is 0.
        Batched so a single request stays under the hosting timeout.
        """
        prompts = list(
            (
                await self.session.execute(
                    select(Prompt).where(Prompt.status == PromptStatus.PUBLISHED)
                )
            )
            .unique()
            .scalars()
            .all()
        )
        have = {
            r.prompt_id for r in (await self.session.execute(select(PromptEmbedding))).scalars()
        }
        missing = [p for p in prompts if p.id not in have]
        embedded = 0
        for prompt in missing[:batch]:
            if await self.reembed(prompt):
                embedded += 1
        return embedded, len(missing) - embedded
