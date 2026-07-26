"""Aggregate router for API v1.

Each feature milestone registers its router here, keeping ``main.py`` clean and
giving a single place to see the full v1 surface.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
    analytics,
    api_keys,
    auth,
    categories,
    collections,
    community,
    health,
    projects,
    prompts,
    public,
    tags,
    teams,
    users,
)
from app.core.ratelimit import rate_limit

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(community.router, tags=["community"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(api_keys.router, prefix="/keys", tags=["api-keys"])
api_router.include_router(
    public.router,
    prefix="/public",
    tags=["public-api"],
    dependencies=[Depends(rate_limit("public_api", "RATE_LIMIT_PUBLIC_PER_MIN", by="key"))],
)
