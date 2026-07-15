"""Project / Module / Component endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Page, PageParams
from app.schemas.project import (
    ComponentCreate,
    ComponentRead,
    ModuleCreate,
    ModuleRead,
    ProjectCreate,
    ProjectRead,
    ProjectTree,
    ProjectUpdate,
)
from app.services.project import ProjectService

router = APIRouter()


# --- Projects ---------------------------------------------------------------
@router.get("", response_model=Page[ProjectRead], summary="List projects")
async def list_projects(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page[ProjectRead]:
    params = PageParams(page=page, size=size)
    items, total = await ProjectService(db).list_projects(
        offset=params.offset, limit=params.limit
    )
    return Page.create([ProjectRead.model_validate(p) for p in items], total, params)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
async def create_project(data: ProjectCreate, db: DbSession, user: CurrentUser) -> ProjectRead:
    project = await ProjectService(db).create_project(data, user)
    return ProjectRead.model_validate(project)


@router.get("/{project_id}/tree", response_model=ProjectTree, summary="Full project tree")
async def project_tree(project_id: uuid.UUID, db: DbSession) -> ProjectTree:
    return await ProjectService(db).get_tree(project_id)


@router.patch("/{project_id}", response_model=ProjectRead, summary="Update a project")
async def update_project(
    project_id: uuid.UUID, data: ProjectUpdate, db: DbSession, user: CurrentUser
) -> ProjectRead:
    project = await ProjectService(db).update_project(project_id, data, user)
    return ProjectRead.model_validate(project)


@router.delete(
    "/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a project"
)
async def delete_project(project_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await ProjectService(db).delete_project(project_id, user)


# --- Modules ----------------------------------------------------------------
@router.post(
    "/{project_id}/modules",
    response_model=ModuleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a module to a project",
)
async def add_module(
    project_id: uuid.UUID, data: ModuleCreate, db: DbSession, user: CurrentUser
) -> ModuleRead:
    module = await ProjectService(db).add_module(project_id, data, user)
    return ModuleRead.model_validate(module)


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a module",
)
async def delete_module(module_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await ProjectService(db).delete_module(module_id, user)


# --- Components -------------------------------------------------------------
@router.post(
    "/modules/{module_id}/components",
    response_model=ComponentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a component to a module",
)
async def add_component(
    module_id: uuid.UUID, data: ComponentCreate, db: DbSession, user: CurrentUser
) -> ComponentRead:
    component = await ProjectService(db).add_component(module_id, data, user)
    return ComponentRead.model_validate(component)


@router.get(
    "/components/{component_id}",
    response_model=ComponentRead,
    summary="Get a component",
)
async def get_component(component_id: uuid.UUID, db: DbSession) -> ComponentRead:
    component = await ProjectService(db).get_component(component_id)
    return ComponentRead.model_validate(component)


@router.delete(
    "/components/{component_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a component",
)
async def delete_component(component_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await ProjectService(db).delete_component(component_id, user)
