"""Liveness/readiness endpoints.

``/health`` is a cheap liveness probe. ``/health/ready`` verifies the database
connection so orchestrators only route traffic once dependencies are reachable.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus, summary="Liveness probe")
async def health() -> HealthStatus:
    return HealthStatus(
        status="ok",
        service=settings.PROJECT_NAME,
        version=__version__,
        environment=settings.ENVIRONMENT,
        database="sqlite" if settings.is_sqlite else "postgresql",
    )


@router.get("/health/ready", response_model=HealthStatus, summary="Readiness probe")
async def readiness(db: AsyncSession = Depends(get_db)) -> HealthStatus:
    await db.execute(text("SELECT 1"))
    return HealthStatus(
        status="ready",
        service=settings.PROJECT_NAME,
        version=__version__,
        environment=settings.ENVIRONMENT,
        database="sqlite" if settings.is_sqlite else "postgresql",
    )
