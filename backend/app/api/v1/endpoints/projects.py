"""Project / Module / Component endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.core.ratelimit import rate_limit
from app.models.enums import KitCategory
from app.schemas.common import Page, PageParams
from app.schemas.project import (
    ComponentCatalogItem,
    ComponentCreate,
    ComponentRead,
    ModuleCreate,
    ModuleRead,
    ProjectCreate,
    ProjectRead,
    ProjectTree,
    ProjectUpdate,
)
from app.schemas.template import (
    PreviewCreate,
    PreviewRead,
    PublicTemplateSummary,
    TemplateRead,
    TemplateUpsert,
)
from app.services.codebase import ArchiveUnavailableError, UnsupportedRepoError, open_archive
from app.services.project import ProjectService
from app.services.template import TemplateService

router = APIRouter()


# --- Starter Kits catalog (public web browsing) -----------------------------
@router.get(
    "/templates",
    response_model=Page[PublicTemplateSummary],
    summary="Browse starter kits (projects with a codebase)",
)
async def browse_templates(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(24, ge=1, le=100),
    category: KitCategory | None = Query(None, description="Filter by kit category"),
) -> Page[PublicTemplateSummary]:
    params = PageParams(page=page, size=size)
    items, total = await TemplateService(db).list_public(
        offset=params.offset,
        limit=params.limit,
        category=category.value if category else None,
    )
    return Page.create(items, total, params)


@router.get(
    "/{project_id}/template/download",
    summary="Download a starter kit's codebase as a zip",
    dependencies=[
        Depends(rate_limit("web_download", "RATE_LIMIT_DOWNLOAD_PER_MIN", by="ip"))
    ],
)
async def download_kit(
    project_id: uuid.UUID,
    db: DbSession,
    ref: str = Query("main", description="Branch, tag, or commit — defaults to latest"),
) -> StreamingResponse:
    service = TemplateService(db)
    info = await service.download_info(project_id)
    if info is None:
        raise NotFoundError("This project is not a template")
    repo_url, slug = info
    try:
        body = await open_archive(repo_url, ref)
    except UnsupportedRepoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ArchiveUnavailableError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, detail=f"Couldn't fetch the codebase: {exc}"
        ) from exc
    await service.count_download(project_id)
    return StreamingResponse(
        body,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
    )


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


# --- Starter template (codebase pointer) ------------------------------------
@router.get(
    "/{project_id}/template",
    response_model=TemplateRead,
    summary="Get a project's starter-template metadata",
)
async def get_template(project_id: uuid.UUID, db: DbSession) -> TemplateRead:
    tpl = await TemplateService(db).get_for_project(project_id)
    if tpl is None:
        raise NotFoundError("This project is not a template")
    return TemplateRead.model_validate(tpl)


@router.put(
    "/{project_id}/template",
    response_model=TemplateRead,
    summary="Mark a project as a starter template (owner only)",
)
async def upsert_template(
    project_id: uuid.UUID, data: TemplateUpsert, db: DbSession, user: CurrentUser
) -> TemplateRead:
    tpl = await TemplateService(db).upsert(project_id, user, data)
    return TemplateRead.model_validate(tpl)


@router.delete(
    "/{project_id}/template",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unmark a project as a template (owner only)",
)
async def delete_template(project_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await TemplateService(db).remove(project_id, user)


# --- Codebase UI previews (screenshots) -------------------------------------
@router.get(
    "/{project_id}/template/previews",
    response_model=list[PreviewRead],
    summary="List a kit's UI preview screenshots",
)
async def list_previews(project_id: uuid.UUID, db: DbSession) -> list[PreviewRead]:
    previews = await TemplateService(db).list_previews(project_id)
    return [PreviewRead.model_validate(p) for p in previews]


@router.post(
    "/{project_id}/template/previews",
    response_model=PreviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a UI preview screenshot (owner only)",
)
async def add_preview(
    project_id: uuid.UUID, data: PreviewCreate, db: DbSession, user: CurrentUser
) -> PreviewRead:
    preview = await TemplateService(db).add_preview(project_id, user, data)
    return PreviewRead.model_validate(preview)


@router.delete(
    "/{project_id}/template/previews/{preview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a UI preview (owner only)",
)
async def delete_preview(
    project_id: uuid.UUID, preview_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> None:
    await TemplateService(db).remove_preview(project_id, preview_id, user)


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
@router.get(
    "/components",
    response_model=Page[ComponentCatalogItem],
    summary="List all components across projects",
)
async def list_components(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100),
) -> Page[ComponentCatalogItem]:
    params = PageParams(page=page, size=size)
    items, total = await ProjectService(db).list_components(
        offset=params.offset, limit=params.limit
    )
    return Page.create(items, total, params)


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
