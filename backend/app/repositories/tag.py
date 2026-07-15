"""Tag data access with get-or-create semantics."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.slug import slugify
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Tag, session)

    async def get_by_slug(self, slug: str) -> Tag | None:
        return await self.get_by(slug=slug)

    async def get_or_create(self, name: str) -> Tag:
        slug = slugify(name)
        existing = await self.get_by_slug(slug)
        if existing:
            return existing
        return await self.create(name=name.strip()[:50], slug=slug, usage_count=0)

    async def resolve_many(self, names: list[str]) -> list[Tag]:
        """Get-or-create a de-duplicated set of tags, preserving input order."""
        seen: set[str] = set()
        tags: list[Tag] = []
        for name in names:
            cleaned = name.strip()
            if not cleaned:
                continue
            slug = slugify(cleaned)
            if slug in seen:
                continue
            seen.add(slug)
            tags.append(await self.get_or_create(cleaned))
        return tags

    async def popular(self, limit: int = 30) -> list[Tag]:
        stmt = (
            select(Tag)
            .where(Tag.usage_count > 0)
            .order_by(Tag.usage_count.desc(), Tag.name)
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_all(self) -> list[Tag]:
        stmt = select(Tag).order_by(Tag.name)
        return list((await self.session.execute(stmt)).scalars().all())
