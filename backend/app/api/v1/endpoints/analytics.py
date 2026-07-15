"""Analytics endpoints (public read)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.models.enums import PromptStatus
from app.repositories.prompt import PromptRepository, SortKey
from app.schemas.analytics import Contributor, GrowthPoint, OverviewStats, TypeCount
from app.schemas.prompt import PromptSummary
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=OverviewStats, summary="Headline totals")
async def overview(db: DbSession) -> OverviewStats:
    return await AnalyticsService(db).overview()


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


@router.get("/growth", response_model=list[GrowthPoint], summary="Prompt growth over time")
async def growth(db: DbSession, days: int = Query(30, ge=7, le=90)) -> list[GrowthPoint]:
    return await AnalyticsService(db).growth(days)


@router.get("/by-type", response_model=list[TypeCount], summary="Prompt count by type")
async def by_type(db: DbSession) -> list[TypeCount]:
    return await AnalyticsService(db).by_type()
