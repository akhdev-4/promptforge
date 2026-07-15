"""Project hierarchy business logic: CRUD, ownership, tree assembly."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.slug import slug_with_suffix
from app.models.project import Component, Module, Project
from app.models.user import User, UserRole
from app.repositories.project import (
    ComponentRepository,
    ModuleRepository,
    ProjectRepository,
)
from app.schemas.project import (
    ComponentCreate,
    ComponentNode,
    ModuleCreate,
    ModuleNode,
    ProjectCreate,
    ProjectTree,
    ProjectUpdate,
)


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.projects = ProjectRepository(session)
        self.modules = ModuleRepository(session)
        self.components = ComponentRepository(session)

    # --- Authorization -------------------------------------------------------
    @staticmethod
    def _can_manage(project: Project, user: User) -> bool:
        return project.author_id == user.id or user.role.satisfies(UserRole.MODERATOR)

    async def _project_or_404(self, project_id: uuid.UUID) -> Project:
        project = await self.projects.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        return project

    async def _owned_project(self, project_id: uuid.UUID, user: User) -> Project:
        project = await self._project_or_404(project_id)
        if not self._can_manage(project, user):
            raise PermissionDeniedError("You cannot modify this project")
        return project

    async def _module_or_404(self, module_id: uuid.UUID) -> Module:
        module = await self.modules.get(module_id)
        if module is None:
            raise NotFoundError("Module not found")
        return module

    async def _component_or_404(self, component_id: uuid.UUID) -> Component:
        component = await self.components.get(component_id)
        if component is None:
            raise NotFoundError("Component not found")
        return component

    # --- Projects ------------------------------------------------------------
    async def create_project(self, data: ProjectCreate, user: User) -> Project:
        return await self.projects.create(
            name=data.name,
            slug=slug_with_suffix(data.name),
            description=data.description,
            icon=data.icon,
            author_id=user.id,
        )

    async def update_project(
        self, project_id: uuid.UUID, data: ProjectUpdate, user: User
    ) -> Project:
        project = await self._owned_project(project_id, user)
        return await self.projects.update(project, **data.model_dump(exclude_unset=True))

    async def delete_project(self, project_id: uuid.UUID, user: User) -> None:
        project = await self._owned_project(project_id, user)
        await self.projects.delete(project)

    async def list_projects(self, *, offset: int, limit: int) -> tuple[list[Project], int]:
        return await self.projects.list_all(offset=offset, limit=limit)

    # --- Modules -------------------------------------------------------------
    async def add_module(
        self, project_id: uuid.UUID, data: ModuleCreate, user: User
    ) -> Module:
        await self._owned_project(project_id, user)
        return await self.modules.create(
            name=data.name,
            slug=slug_with_suffix(data.name),
            description=data.description,
            position=data.position,
            project_id=project_id,
        )

    async def delete_module(self, module_id: uuid.UUID, user: User) -> None:
        module = await self._module_or_404(module_id)
        await self._owned_project(module.project_id, user)
        await self.modules.delete(module)

    # --- Components ----------------------------------------------------------
    async def add_component(
        self, module_id: uuid.UUID, data: ComponentCreate, user: User
    ) -> Component:
        module = await self._module_or_404(module_id)
        await self._owned_project(module.project_id, user)
        return await self.components.create(
            name=data.name,
            slug=slug_with_suffix(data.name),
            description=data.description,
            position=data.position,
            module_id=module_id,
        )

    async def delete_component(self, component_id: uuid.UUID, user: User) -> None:
        component = await self._component_or_404(component_id)
        module = await self._module_or_404(component.module_id)
        await self._owned_project(module.project_id, user)
        await self.components.delete(component)

    # --- Tree ----------------------------------------------------------------
    async def get_tree(self, project_id: uuid.UUID) -> ProjectTree:
        project = await self._project_or_404(project_id)
        modules = await self.modules.for_project(project_id)
        components = await self.components.for_modules([m.id for m in modules])
        counts = await self.components.prompt_counts([c.id for c in components])

        components_by_module: dict[uuid.UUID, list[ComponentNode]] = {}
        for c in components:
            components_by_module.setdefault(c.module_id, []).append(
                ComponentNode(
                    id=c.id,
                    name=c.name,
                    slug=c.slug,
                    description=c.description,
                    position=c.position,
                    prompt_count=counts.get(c.id, 0),
                )
            )

        module_nodes = [
            ModuleNode(
                id=m.id,
                name=m.name,
                slug=m.slug,
                description=m.description,
                position=m.position,
                components=components_by_module.get(m.id, []),
            )
            for m in modules
        ]
        return ProjectTree(
            id=project.id,
            name=project.name,
            slug=project.slug,
            description=project.description,
            icon=project.icon,
            author=project.author,  # type: ignore[arg-type]
            created_at=project.created_at,
            modules=module_nodes,
        )

    async def get_component(self, component_id: uuid.UUID) -> Component:
        return await self._component_or_404(component_id)
