"""Prompt CRUD, versioning, copy, and fork endpoints."""

from __future__ import annotations

import contextlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import (
    CurrentUser,
    DbSession,
    OptionalUser,
    require_admin,
    require_contributor,
)
from app.core.exceptions import NotFoundError
from app.models.enums import PromptStatus, PromptType
from app.models.user import User
from app.playground import get_run_provider, render_prompt
from app.recommendations import get_related_provider
from app.repositories.prompt import SortKey
from app.schemas.asset import AssetCreate, AssetRead, VersionCompare
from app.schemas.collection import BookmarkResponse, LikeResponse
from app.schemas.common import Page, PageParams
from app.schemas.playground import PlaygroundRunRequest, PlaygroundRunResult
from app.schemas.prompt import (
    PromptContent,
    PromptCreate,
    PromptDetail,
    PromptSummary,
    PromptUpdate,
    PromptVersionRead,
    RatingCreate,
    RatingResult,
    VersionCreate,
)
from app.services.interaction import InteractionService
from app.services.prompt import PromptService
from app.services.semantic import SemanticSearchService
from app.services.team import TeamService

router = APIRouter()


async def _embed_best_effort(db: DbSession, prompt) -> None:
    """Compute a prompt's semantic embedding for search, isolated in a savepoint
    so a failure (rate limit, no key) never breaks the create/update request."""
    with contextlib.suppress(Exception):
        async with db.begin_nested():
            await SemanticSearchService(db).reembed(prompt)


@router.post(
    "",
    response_model=PromptDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a prompt (seeds version 1)",
)
async def create_prompt(
    data: PromptCreate,
    db: DbSession,
    user: Annotated[User, Depends(require_contributor)],
) -> PromptDetail:
    prompt = await PromptService(db).create(data, user)
    if data.team_id is not None:
        await TeamService(db).assign_prompt(prompt.id, data.team_id, user)
    else:
        # Only public prompts are embedded for search.
        await _embed_best_effort(db, prompt)
    detail = PromptDetail.model_validate(prompt)
    detail.team_id = data.team_id
    return detail


@router.get("", response_model=Page[PromptSummary], summary="List / search prompts")
async def list_prompts(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, description="Full-text-ish search over title/description/content"),
    prompt_type: PromptType | None = None,
    framework: str | None = None,
    language: str | None = None,
    ai_model: str | None = None,
    status: PromptStatus | None = PromptStatus.PUBLISHED,
    author_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = Query(None, description="Includes descendant categories"),
    exclude_category_id: uuid.UUID | None = Query(
        None, description="Excludes this category and its descendants (keeps uncategorized)"
    ),
    component_id: uuid.UUID | None = Query(None, description="Variants in a component"),
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
        ai_model=ai_model,
        status=status,
        author_id=author_id,
        category_id=category_id,
        exclude_category_id=exclude_category_id,
        component_id=component_id,
        tags=tags,
        sort=sort,
    )
    return Page.create([PromptSummary.model_validate(p) for p in items], total, params)


@router.get(
    "/semantic",
    response_model=list[PromptSummary],
    summary="Meaning-based search (falls back to keyword search)",
)
async def semantic_search(
    db: DbSession,
    q: str = Query(..., min_length=1),
    limit: int = Query(8, ge=1, le=20),
) -> list[PromptSummary]:
    results = await SemanticSearchService(db).search(q, limit=limit)
    if results is None:  # no embeddings / no key -> keyword fallback
        results, _ = await PromptService(db).search(offset=0, limit=limit, q=q)
    return [PromptSummary.model_validate(p) for p in results]


@router.post(
    "/embeddings/backfill",
    dependencies=[Depends(require_admin)],
    summary="Embed a batch of prompts missing an embedding (admin)",
)
async def backfill_embeddings(
    db: DbSession, limit: int = Query(20, ge=1, le=50)
) -> dict[str, int]:
    embedded, remaining = await SemanticSearchService(db).backfill(batch=limit)
    return {"embedded": embedded, "remaining": remaining}


@router.get("/{prompt_id}", response_model=PromptDetail, summary="Get a prompt (counts a view)")
async def get_prompt(
    prompt_id: uuid.UUID, db: DbSession, user: OptionalUser
) -> PromptDetail:
    # Private (team) prompts are visible only to that team's members; otherwise
    # 404 so we don't reveal their existence.
    teams = TeamService(db)
    team_id = await teams.team_of_prompt(prompt_id)
    if team_id is not None and (
        user is None or not await teams.is_member(team_id, user.id)
    ):
        raise NotFoundError("Prompt not found")

    prompt = await PromptService(db).get_detail(prompt_id)
    detail = PromptDetail.model_validate(prompt)
    detail.team_id = team_id
    if user is not None:
        interactions = InteractionService(db)
        liked, bookmarked = await interactions.flags(user.id, prompt_id)
        detail.is_liked = liked
        detail.is_bookmarked = bookmarked
        detail.my_rating = await interactions.my_rating(user.id, prompt_id)
    return detail


@router.get(
    "/{prompt_id}/related",
    response_model=list[PromptSummary],
    summary="Related / similar prompts (recommendations)",
)
async def related_prompts(
    prompt_id: uuid.UUID, db: DbSession, limit: int = Query(6, ge=1, le=20)
) -> list[PromptSummary]:
    service = PromptService(db)
    prompt = await service.get_detail(prompt_id, count_view=False)
    provider = get_related_provider()
    related = await provider.related(db, prompt, limit=limit)
    return [PromptSummary.model_validate(p) for p in related]


@router.patch("/{prompt_id}", response_model=PromptDetail, summary="Update prompt metadata")
async def update_prompt(
    prompt_id: uuid.UUID, data: PromptUpdate, db: DbSession, user: CurrentUser
) -> PromptDetail:
    prompt = await PromptService(db).update_metadata(prompt_id, data, user)
    await _embed_best_effort(db, prompt)
    return PromptDetail.model_validate(prompt)


@router.delete(
    "/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a prompt"
)
async def delete_prompt(prompt_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await PromptService(db).delete(prompt_id, user)


@router.post(
    "/{prompt_id}/copy",
    response_model=PromptContent,
    summary="Copy a prompt (counts a copy)",
)
async def copy_prompt(prompt_id: uuid.UUID, db: DbSession) -> PromptContent:
    prompt = await PromptService(db).copy(prompt_id)
    return PromptContent(id=prompt.id, content=prompt.content, copies_count=prompt.copies_count)


@router.post("/{prompt_id}/like", response_model=LikeResponse, summary="Toggle like")
async def toggle_like(prompt_id: uuid.UUID, db: DbSession, user: CurrentUser) -> LikeResponse:
    liked, count = await InteractionService(db).toggle_like(user.id, prompt_id)
    return LikeResponse(liked=liked, likes_count=count)


@router.post("/{prompt_id}/bookmark", response_model=BookmarkResponse, summary="Toggle bookmark")
async def toggle_bookmark(
    prompt_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> BookmarkResponse:
    bookmarked = await InteractionService(db).toggle_bookmark(user.id, prompt_id)
    return BookmarkResponse(bookmarked=bookmarked)


@router.post(
    "/{prompt_id}/run",
    response_model=PlaygroundRunResult,
    summary="Run a prompt in the Playground",
)
async def run_prompt(
    prompt_id: uuid.UUID, data: PlaygroundRunRequest, db: DbSession, user: CurrentUser
) -> PlaygroundRunResult:
    prompt = await PromptService(db).get_detail(prompt_id, count_view=False)
    rendered = render_prompt(prompt.content, data.variables)
    try:
        result = await get_run_provider(data.mode).run(rendered)
    except Exception as exc:  # noqa: BLE001 - surface any provider failure cleanly
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"The model provider couldn't be reached: {exc}",
        ) from exc
    return PlaygroundRunResult(
        output=result.output,
        rendered_prompt=rendered,
        provider=result.provider,
        model=result.model,
        is_demo=result.is_demo,
        image_url=result.image_url,
    )


@router.post("/{prompt_id}/run/stream", summary="Run a prompt with streamed text output")
async def run_prompt_stream(
    prompt_id: uuid.UUID, data: PlaygroundRunRequest, db: DbSession, user: CurrentUser
) -> StreamingResponse:
    prompt = await PromptService(db).get_detail(prompt_id, count_view=False)
    rendered = render_prompt(prompt.content, data.variables)
    provider = get_run_provider("text")

    async def gen():
        try:
            async for chunk in provider.stream(rendered):  # type: ignore[attr-defined]
                yield chunk
        except Exception as exc:  # noqa: BLE001 - surface stream failures inline
            yield f"\n\n⚠️ {exc}"

    return StreamingResponse(
        gen(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@router.post("/{prompt_id}/rating", response_model=RatingResult, summary="Rate a prompt (1-5)")
async def rate_prompt(
    prompt_id: uuid.UUID, data: RatingCreate, db: DbSession, user: CurrentUser
) -> RatingResult:
    avg, count, mine = await InteractionService(db).rate(user.id, prompt_id, data.stars)
    return RatingResult(rating_avg=avg, rating_count=count, my_rating=mine)


@router.delete("/{prompt_id}/rating", response_model=RatingResult, summary="Remove your rating")
async def unrate_prompt(
    prompt_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> RatingResult:
    avg, count = await InteractionService(db).unrate(user.id, prompt_id)
    return RatingResult(rating_avg=avg, rating_count=count, my_rating=None)


@router.post(
    "/{prompt_id}/fork",
    response_model=PromptDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Fork a prompt into your library",
)
async def fork_prompt(
    prompt_id: uuid.UUID,
    db: DbSession,
    user: Annotated[User, Depends(require_contributor)],
) -> PromptDetail:
    fork = await PromptService(db).fork(prompt_id, user)
    return PromptDetail.model_validate(fork)


# --- Versions ---------------------------------------------------------------
@router.post(
    "/{prompt_id}/versions",
    response_model=PromptVersionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new version",
)
async def add_version(
    prompt_id: uuid.UUID, data: VersionCreate, db: DbSession, user: CurrentUser
) -> PromptVersionRead:
    _, version = await PromptService(db).add_version(prompt_id, data, user)
    return PromptVersionRead.model_validate(version)


@router.get(
    "/{prompt_id}/versions",
    response_model=list[PromptVersionRead],
    summary="List versions (newest first)",
)
async def list_versions(prompt_id: uuid.UUID, db: DbSession) -> list[PromptVersionRead]:
    versions = await PromptService(db).list_versions(prompt_id)
    return [PromptVersionRead.model_validate(v) for v in versions]


@router.get(
    "/{prompt_id}/versions/compare",
    response_model=VersionCompare,
    summary="Compare two versions (line diff)",
)
async def compare_versions(
    prompt_id: uuid.UUID,
    db: DbSession,
    from_: int = Query(..., alias="from", ge=1),
    to: int = Query(..., ge=1),
) -> VersionCompare:
    return await PromptService(db).compare_versions(prompt_id, from_, to)


@router.get(
    "/{prompt_id}/versions/{version_number}",
    response_model=PromptVersionRead,
    summary="Get a specific version",
)
async def get_version(
    prompt_id: uuid.UUID, version_number: int, db: DbSession
) -> PromptVersionRead:
    version = await PromptService(db).get_version(prompt_id, version_number)
    return PromptVersionRead.model_validate(version)


# --- Assets -----------------------------------------------------------------
@router.get(
    "/{prompt_id}/assets",
    response_model=list[AssetRead],
    summary="List a prompt's preview assets",
)
async def list_assets(prompt_id: uuid.UUID, db: DbSession) -> list[AssetRead]:
    assets = await PromptService(db).list_assets(prompt_id)
    return [AssetRead.model_validate(a) for a in assets]


@router.post(
    "/{prompt_id}/assets",
    response_model=AssetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Attach a preview asset (owner/moderator)",
)
async def add_asset(
    prompt_id: uuid.UUID, data: AssetCreate, db: DbSession, user: CurrentUser
) -> AssetRead:
    asset = await PromptService(db).add_asset(prompt_id, data, user)
    return AssetRead.model_validate(asset)


@router.delete(
    "/{prompt_id}/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a preview asset (owner/moderator)",
)
async def delete_asset(
    prompt_id: uuid.UUID, asset_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> None:
    await PromptService(db).delete_asset(prompt_id, asset_id, user)
