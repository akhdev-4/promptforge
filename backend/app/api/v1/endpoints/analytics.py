"""Analytics endpoints.

Trending / latest / contributors stay global — they power the Dashboard's view
of the whole library. Overview, growth and by-type are personal: they answer
"how is *my* work doing", so they require a signed-in user and are scoped to it.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models.enums import PromptStatus
from app.repositories.prompt import PromptRepository, SortKey
from app.schemas.analytics import Contributor, GrowthPoint, OverviewStats, TypeCount
from app.schemas.prompt import PromptSummary
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get(
    "/overview",
    response_model=OverviewStats,
    summary="Headline totals for your own prompts",
)
async def overview(db: DbSession, user: CurrentUser) -> OverviewStats:
    return await AnalyticsService(db).overview(author_id=user.id)


@router.get(
    "/trending",
    response_model=list[PromptSummary],
    summary="Trending prompts (most copied)",
)
async def trending(db: DbSession, limit: int = Query(6, ge=1, le=20)) -> list[PromptSummary]:
    prompts, _ = await PromptRepository(db).search(
        offset=0, limit=limit, status=PromptStatus.PUBLISHED, sort="most_copied"
    )
    return [PromptSummary.model_validate(p) for p in prompts]


@router.get(
    "/latest",
    response_model=list[PromptSummary],
    summary="Latest prompts",
)
async def latest(db: DbSession, limit: int = Query(6, ge=1, le=20)) -> list[PromptSummary]:
    sort: SortKey = "newest"
    prompts, _ = await PromptRepository(db).search(
        offset=0, limit=limit, status=PromptStatus.PUBLISHED, sort=sort
    )
    return [PromptSummary.model_validate(p) for p in prompts]


@router.get(
    "/contributors",
    response_model=list[Contributor],
    summary="Top contributors",
)
async def contributors(db: DbSession, limit: int = Query(5, ge=1, le=20)) -> list[Contributor]:
    return await AnalyticsService(db).top_contributors(limit)


@router.get(
    "/growth",
    response_model=list[GrowthPoint],
    summary="Your prompt growth over time",
)
async def growth(
    db: DbSession, user: CurrentUser, days: int = Query(30, ge=7, le=90)
) -> list[GrowthPoint]:
    return await AnalyticsService(db).growth(days, author_id=user.id)


@router.get(
    "/by-type",
    response_model=list[TypeCount],
    summary="Your prompt count by type",
)
async def by_type(db: DbSession, user: CurrentUser) -> list[TypeCount]:
    return await AnalyticsService(db).by_type(author_id=user.id)
