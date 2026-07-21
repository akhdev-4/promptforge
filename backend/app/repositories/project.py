"""Data access for the Project → Module → Component hierarchy."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Component, Module, Project
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Project, session)

    async def get_by_slug(self, slug: str) -> Project | None:
        return await self.get_by(slug=slug)

    async def list_all(self, *, offset: int, limit: int) -> tuple[list[Project], int]:
        total = int(
            (await self.session.execute(select(func.count()).select_from(Project))).scalar_one()
        )
        stmt = select(Project).order_by(Project.created_at.desc()).offset(offset).limit(limit)
        rows = list((await self.session.execute(stmt)).unique().scalars().all())
        return rows, total


class ModuleRepository(BaseRepository[Module]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Module, session)

    async def for_project(self, project_id: uuid.UUID) -> list[Module]:
        stmt = (
            select(Module)
            .where(Module.project_id == project_id)
            .order_by(Module.position, Module.name)
        )
        return list((await self.session.execute(stmt)).scalars().all())


class ComponentRepository(BaseRepository[Component]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Component, session)

    async def for_modules(self, module_ids: list[uuid.UUID]) -> list[Component]:
        if not module_ids:
            return []
        stmt = (
            select(Component)
            .where(Component.module_id.in_(module_ids))
            .order_by(Component.position, Component.name)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_catalog(self, *, offset: int, limit: int) -> tuple[list, int]:
        """All components across every project, with their module/project context."""
        total = int(
            (await self.session.execute(select(func.count()).select_from(Component))).scalar_one()
        )
        stmt = (
            select(
                Component,
                Module.name.label("module_name"),
                Project.id.label("project_id"),
                Project.name.label("project_name"),
            )
            .join(Module, Component.module_id == Module.id)
            .join(Project, Module.project_id == Project.id)
            .order_by(Component.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await self.session.execute(stmt)).all())
        return rows, total

    async def prompt_counts(self, component_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        """Published prompt count per component."""
        if not component_ids:
            return {}
        stmt = (
            select(Prompt.component_id, func.count())
            .where(Prompt.component_id.in_(component_ids))
            .group_by(Prompt.component_id)
        )
        rows = await self.session.execute(stmt)
        return {cid: count for cid, count in rows.all() if cid is not None}
