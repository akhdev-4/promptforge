"""Public API — read-only prompt access authenticated by an API key.

This is the surface the CLI and IDE plugin consume. Every route requires a valid
``X-API-Key`` and only ever exposes *published, non-private* prompts, so a key
can never reach team-private content or drafts.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import ApiKeyUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.enums import KitCategory, PromptStatus, PromptType
from app.repositories.prompt import SortKey
from app.schemas.common import Page, PageParams
from app.schemas.prompt import PromptDetail, PromptSummary
from app.schemas.template import PublicTemplateManifest, PublicTemplateSummary
from app.schemas.user import UserPublic
from app.services.codebase import ArchiveUnavailableError, UnsupportedRepoError, open_archive
from app.services.prompt import PromptService
from app.services.team import TeamService
from app.services.template import TemplateService

router = APIRouter()


@router.get("/me", response_model=UserPublic, summary="Identity behind the API key")
async def whoami(user: ApiKeyUser) -> UserPublic:
    return UserPublic.model_validate(user)


@router.get(
    "/prompts",
    response_model=Page[PromptSummary],
    summary="List / search published prompts",
)
async def list_prompts(
    db: DbSession,
    _user: ApiKeyUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, description="Search over title/description/content"),
    prompt_type: PromptType | None = None,
    framework: str | None = None,
    language: str | None = None,
    tags: list[str] | None = Query(None, description="Tag slugs; matches any"),
    sort: SortKey = "newest",
) -> Page[PromptSummary]:
    params = PageParams(page=page, size=size)
    items, total = await PromptService(db).search(
        offset=params.offset,
        limit=params.limit,
        q=q,
        prompt_type=prompt_type,
        framework=framework,
        language=language,
        status=PromptStatus.PUBLISHED,  # public API never exposes drafts
        tags=tags,
        sort=sort,
    )
    return Page.create([PromptSummary.model_validate(p) for p in items], total, params)


@router.get(
    "/prompts/{prompt_id}",
    response_model=PromptDetail,
    summary="Get a published prompt with full content",
)
async def get_prompt(prompt_id: uuid.UUID, db: DbSession, _user: ApiKeyUser) -> PromptDetail:
    # Private (team) prompts are never reachable via a key — 404, don't reveal.
    if await TeamService(db).team_of_prompt(prompt_id) is not None:
        raise NotFoundError("Prompt not found")
    prompt = await PromptService(db).get_detail(prompt_id, count_view=False)
    if prompt.status != PromptStatus.PUBLISHED:
        raise NotFoundError("Prompt not found")
    return PromptDetail.model_validate(prompt)


@router.get(
    "/templates",
    response_model=Page[PublicTemplateSummary],
    summary="List starter templates (projects with a codebase)",
)
async def list_templates(
    db: DbSession,
    _user: ApiKeyUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
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
    "/templates/{project_id}",
    response_model=PublicTemplateManifest,
    summary="Full template manifest (code pointer + prompt map) for the CLI",
)
async def get_template(
    project_id: uuid.UUID, db: DbSession, _user: ApiKeyUser
) -> PublicTemplateManifest:
    return await TemplateService(db).get_manifest(project_id)


@router.get(
    "/templates/{project_id}/download",
    summary="Download the kit's codebase as a zip (streamed through PromptForge)",
)
async def download_template(
    project_id: uuid.UUID,
    db: DbSession,
    _user: ApiKeyUser,
    ref: str = Query("main", description="Branch, tag, or commit — defaults to latest"),
) -> StreamingResponse:
    info = await TemplateService(db).download_info(project_id)
    if info is None:
        raise NotFoundError("Template not found")
    repo_url, slug = info
    try:
        body = await open_archive(repo_url, ref)
    except UnsupportedRepoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ArchiveUnavailableError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Couldn't fetch the codebase: {exc}",
        ) from exc
    return StreamingResponse(
        body,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
    )
