"""Category data access, including tree/descendant helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Category, session)

    async def get_by_slug(self, slug: str) -> Category | None:
        return await self.get_by(slug=slug)

    async def slug_exists(self, slug: str) -> bool:
        return (await self.get_by(slug=slug)) is not None

    async def all_ordered(self) -> list[Category]:
        stmt = select(Category).order_by(Category.position, Category.name)
        return list((await self.session.execute(stmt)).scalars().all())

    async def descendant_ids(self, root_id: uuid.UUID) -> list[uuid.UUID]:
        """Return ``root_id`` plus all descendant ids.

        Portable across SQLite/Postgres: loads the (small) category set once and
        walks it in memory instead of relying on a recursive CTE.
        """
        rows = await self.all_ordered()
        children: dict[uuid.UUID | None, list[uuid.UUID]] = {}
        for c in rows:
            children.setdefault(c.parent_id, []).append(c.id)

        result: list[uuid.UUID] = []
        stack = [root_id]
        while stack:
            current = stack.pop()
            result.append(current)
            stack.extend(children.get(current, []))
        return result
