"""Heuristic related-prompt provider.

Scores candidates by overlap with the source prompt and light popularity:

    score = 3·(shared tags) + 2·(same component) + 2·(same category)
            + 1·(same type) + 0.5·log1p(copies)

Candidates are pre-filtered to those sharing at least one signal, keeping the
scored set small. Swap for a vector/embedding provider later behind the same
protocol.
"""

from __future__ import annotations

import math

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromptStatus
from app.models.prompt import Prompt
from app.models.tag import Tag, prompt_tags
from app.models.team import PromptTeam


class HeuristicRelatedProvider:
    async def related(
        self, session: AsyncSession, prompt: Prompt, *, limit: int
    ) -> list[Prompt]:
        target_tag_ids = [t.id for t in prompt.tags]
        target_tag_slugs = {t.slug for t in prompt.tags}

        # Ids of prompts sharing at least one tag with the target.
        tagged_ids: set = set()
        if target_tag_ids:
            rows = await session.execute(
                select(prompt_tags.c.prompt_id)
                .join(Tag, Tag.id == prompt_tags.c.tag_id)
                .where(Tag.id.in_(target_tag_ids))
            )
            tagged_ids = {r[0] for r in rows.all()}

        signals = [Prompt.prompt_type == prompt.prompt_type]
        if prompt.category_id:
            signals.append(Prompt.category_id == prompt.category_id)
        if prompt.component_id:
            signals.append(Prompt.component_id == prompt.component_id)
        if tagged_ids:
            signals.append(Prompt.id.in_(tagged_ids))

        stmt = (
            select(Prompt)
            .where(
                Prompt.id != prompt.id,
                Prompt.status == PromptStatus.PUBLISHED,
                Prompt.id.notin_(select(PromptTeam.prompt_id)),  # exclude private
                or_(*signals),
            )
            .limit(200)
        )
        candidates = list((await session.execute(stmt)).unique().scalars().all())

        def score(c: Prompt) -> float:
            shared_tags = len({t.slug for t in c.tags} & target_tag_slugs)
            s = 3.0 * shared_tags
            if prompt.component_id and c.component_id == prompt.component_id:
                s += 2.0
            if prompt.category_id and c.category_id == prompt.category_id:
                s += 2.0
            if c.prompt_type == prompt.prompt_type:
                s += 1.0
            s += 0.5 * math.log1p(c.copies_count)
            return s

        candidates.sort(key=score, reverse=True)
        return candidates[:limit]
