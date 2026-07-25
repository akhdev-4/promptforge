"""Starter template business logic: owner management + public manifest."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.enums import PromptStatus
from app.models.project import Component, Module, Project
from app.models.prompt import Prompt
from app.models.team import PromptTeam
from app.models.template import ProjectTemplate
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.project import ProjectAuthor
from app.schemas.template import (
    ManifestComponent,
    ManifestModule,
    ManifestPrompt,
    PublicTemplateManifest,
    PublicTemplateSummary,
    TemplateUpsert,
)
from app.services.project import ProjectService

# Only published, non-private prompts are ever exposed through a template.
_PUBLIC_PROMPT = (Prompt.status == PromptStatus.PUBLISHED) & Prompt.id.notin_(
    select(PromptTeam.prompt_id)
)


class TemplateService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.templates = BaseRepository(ProjectTemplate, session)
        self.projects = ProjectService(session)

    # --- Owner management ----------------------------------------------------
    async def upsert(
        self, project_id: uuid.UUID, user: User, data: TemplateUpsert
    ) -> ProjectTemplate:
        await self.projects._owned_project(project_id, user)  # 404 / 403 guard
        existing = await self.templates.get_by(project_id=project_id)
        if existing:
            return await self.templates.update(existing, **data.model_dump())
        return await self.templates.create(project_id=project_id, **data.model_dump())

    async def get_for_project(self, project_id: uuid.UUID) -> ProjectTemplate | None:
        return await self.templates.get_by(project_id=project_id)

    async def remove(self, project_id: uuid.UUID, user: User) -> None:
        await self.projects._owned_project(project_id, user)
        existing = await self.templates.get_by(project_id=project_id)
        if existing is None:
            raise NotFoundError("This project is not a template")
        await self.templates.delete(existing)

    # --- Public catalog ------------------------------------------------------
    async def _prompt_counts(self, project_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        if not project_ids:
            return {}
        stmt = (
            select(Module.project_id, func.count(Prompt.id))
            .select_from(Prompt)
            .join(Component, Prompt.component_id == Component.id)
            .join(Module, Component.module_id == Module.id)
            .where(Module.project_id.in_(project_ids), _PUBLIC_PROMPT)
            .group_by(Module.project_id)
        )
        rows = (await self.session.execute(stmt)).all()
        return {pid: int(n) for pid, n in rows}

    async def list_public(
        self, *, offset: int, limit: int
    ) -> tuple[list[PublicTemplateSummary], int]:
        base = (
            select(ProjectTemplate, Project)
            .join(Project, ProjectTemplate.project_id == Project.id)
            .order_by(ProjectTemplate.created_at.desc())
        )
        total = int(
            (
                await self.session.execute(
                    select(func.count()).select_from(ProjectTemplate)
                )
            ).scalar_one()
        )
        rows = (
            (await self.session.execute(base.offset(offset).limit(limit)))
            .unique()
            .all()
        )
        counts = await self._prompt_counts([proj.id for _, proj in rows])
        items = [
            PublicTemplateSummary(
                project_id=proj.id,
                name=proj.name,
                slug=proj.slug,
                description=proj.description,
                icon=proj.icon,
                stack=tpl.stack,
                repo_url=tpl.repo_url,
                prompt_count=counts.get(proj.id, 0),
                author=ProjectAuthor.model_validate(proj.author),
            )
            for tpl, proj in rows
        ]
        return items, total

    async def get_manifest(self, project_id: uuid.UUID) -> PublicTemplateManifest:
        tpl = await self.templates.get_by(project_id=project_id)
        if tpl is None:
            raise NotFoundError("Template not found")
        project = await self.projects._project_or_404(project_id)

        # Pull the whole module→component→prompt tree in three flat queries.
        modules = list(
            (
                await self.session.execute(
                    select(Module)
                    .where(Module.project_id == project_id)
                    .order_by(Module.position)
                )
            )
            .scalars()
            .all()
        )
        module_ids = [m.id for m in modules]
        components = (
            list(
                (
                    await self.session.execute(
                        select(Component)
                        .where(Component.module_id.in_(module_ids))
                        .order_by(Component.position)
                    )
                )
                .scalars()
                .all()
            )
            if module_ids
            else []
        )
        component_ids = [c.id for c in components]
        prompts = (
            list(
                (
                    await self.session.execute(
                        select(Prompt).where(
                            Prompt.component_id.in_(component_ids), _PUBLIC_PROMPT
                        )
                    )
                )
                .scalars()
                .all()
            )
            if component_ids
            else []
        )

        prompts_by_component: dict[uuid.UUID, list[ManifestPrompt]] = {}
        for p in prompts:
            prompts_by_component.setdefault(p.component_id, []).append(
                ManifestPrompt(id=p.id, slug=p.slug, title=p.title)
            )
        components_by_module: dict[uuid.UUID, list[ManifestComponent]] = {}
        for c in components:
            components_by_module.setdefault(c.module_id, []).append(
                ManifestComponent(
                    name=c.name,
                    slug=c.slug,
                    prompts=prompts_by_component.get(c.id, []),
                )
            )

        return PublicTemplateManifest(
            project_id=project.id,
            name=project.name,
            slug=project.slug,
            description=project.description,
            icon=project.icon,
            stack=tpl.stack,
            repo_url=tpl.repo_url,
            setup_command=tpl.setup_command,
            notes=tpl.notes,
            prompt_count=len(prompts),
            author=ProjectAuthor.model_validate(project.author),
            modules=[
                ManifestModule(
                    name=m.name,
                    slug=m.slug,
                    components=components_by_module.get(m.id, []),
                )
                for m in modules
            ],
        )
