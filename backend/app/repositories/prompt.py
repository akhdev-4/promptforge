"""Prompt data access with filtering, search, and sorting."""

from __future__ import annotations

import uuid
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromptStatus, PromptType
from app.models.prompt import Prompt, PromptVersion
from app.models.tag import Tag, prompt_tags
from app.repositories.base import BaseRepository

SortKey = Literal["newest", "oldest", "most_viewed", "most_copied", "most_liked", "title"]

_SORT_COLUMNS = {
    "newest": Prompt.created_at.desc(),
    "oldest": Prompt.created_at.asc(),
    "most_viewed": Prompt.views_count.desc(),
    "most_copied": Prompt.copies_count.desc(),
    "most_liked": Prompt.likes_count.desc(),
    "title": Prompt.title.asc(),
}


class PromptRepository(BaseRepository[Prompt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Prompt, session)

    async def get_by_slug(self, slug: str) -> Prompt | None:
        return await self.get_by(slug=slug)

    async def slug_exists(self, slug: str) -> bool:
        return (await self.get_by(slug=slug)) is not None

    def _apply_filters(
        self,
        stmt,
        *,
        q: str | None,
        prompt_type: PromptType | None,
        framework: str | None,
        language: str | None,
        ai_model: str | None,
        status: PromptStatus | None,
        author_id: uuid.UUID | None,
        category_ids: list[uuid.UUID] | None = None,
        exclude_category_ids: list[uuid.UUID] | None = None,
        tag_slugs: list[str] | None = None,
        component_id: uuid.UUID | None = None,
    ):
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Prompt.title).like(like),
                    func.lower(func.coalesce(Prompt.description, "")).like(like),
                    func.lower(Prompt.content).like(like),
                )
            )
        if prompt_type:
            stmt = stmt.where(Prompt.prompt_type == prompt_type)
        if framework:
            stmt = stmt.where(func.lower(Prompt.framework) == framework.lower())
        if language:
            stmt = stmt.where(func.lower(Prompt.language) == language.lower())
        if ai_model:
            stmt = stmt.where(func.lower(Prompt.ai_model) == ai_model.lower())
        if status:
            stmt = stmt.where(Prompt.status == status)
        if author_id:
            stmt = stmt.where(Prompt.author_id == author_id)
        if category_ids:
            stmt = stmt.where(Prompt.category_id.in_(category_ids))
        if exclude_category_ids:
            # Keep uncategorized prompts: NULL category is not "in" the excluded
            # set, but SQL NOT IN would drop NULLs, so allow them explicitly.
            stmt = stmt.where(
                or_(
                    Prompt.category_id.is_(None),
                    Prompt.category_id.notin_(exclude_category_ids),
                )
            )
        if component_id:
            stmt = stmt.where(Prompt.component_id == component_id)
        if tag_slugs:
            # Match prompts carrying ANY of the requested tags. A subquery keeps
            # the count/list statements free of join-induced duplicate rows.
            tagged = (
                select(prompt_tags.c.prompt_id)
                .join(Tag, Tag.id == prompt_tags.c.tag_id)
                .where(Tag.slug.in_(tag_slugs))
            )
            stmt = stmt.where(Prompt.id.in_(tagged))
        return stmt

    async def search(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        prompt_type: PromptType | None = None,
        framework: str | None = None,
        language: str | None = None,
        ai_model: str | None = None,
        status: PromptStatus | None = PromptStatus.PUBLISHED,
        author_id: uuid.UUID | None = None,
        category_ids: list[uuid.UUID] | None = None,
        exclude_category_ids: list[uuid.UUID] | None = None,
        tag_slugs: list[str] | None = None,
        component_id: uuid.UUID | None = None,
        sort: SortKey = "newest",
    ) -> tuple[list[Prompt], int]:
        filters = {
            "q": q,
            "prompt_type": prompt_type,
            "framework": framework,
            "language": language,
            "ai_model": ai_model,
            "status": status,
            "author_id": author_id,
            "category_ids": category_ids,
            "exclude_category_ids": exclude_category_ids,
            "tag_slugs": tag_slugs,
            "component_id": component_id,
        }
        base = self._apply_filters(select(Prompt), **filters)
        count_stmt = self._apply_filters(select(func.count()).select_from(Prompt), **filters)
        total = int((await self.session.execute(count_stmt)).scalar_one())

        stmt = base.order_by(_SORT_COLUMNS[sort]).offset(offset).limit(limit)
        rows = list((await self.session.execute(stmt)).unique().scalars().all())
        return rows, total

    async def increment(self, prompt: Prompt, field: str, by: int = 1) -> None:
        setattr(prompt, field, getattr(prompt, field) + by)
        self.session.add(prompt)
        await self.session.flush()
        # Refresh so server-side columns (e.g. updated_at onupdate) are loaded
        # within the async context — avoids lazy IO during response serialization.
        await self.session.refresh(prompt)


class PromptVersionRepository(BaseRepository[PromptVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PromptVersion, session)

    async def list_for_prompt(self, prompt_id: uuid.UUID) -> list[PromptVersion]:
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_version(
        self, prompt_id: uuid.UUID, version_number: int
    ) -> PromptVersion | None:
        return await self.get_by(prompt_id=prompt_id, version_number=version_number)
