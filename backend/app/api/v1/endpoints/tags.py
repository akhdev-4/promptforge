"""Tag endpoints: list all and popular."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.repositories.tag import TagRepository
from app.schemas.tag import TagRead

router = APIRouter()


@router.get("", response_model=list[TagRead], summary="List all tags")
async def list_tags(db: DbSession) -> list[TagRead]:
    tags = await TagRepository(db).list_all()
    return [TagRead.model_validate(t) for t in tags]


@router.get("/popular", response_model=list[TagRead], summary="Most-used tags")
async def popular_tags(db: DbSession, limit: int = Query(30, ge=1, le=100)) -> list[TagRead]:
    tags = await TagRepository(db).popular(limit)
    return [TagRead.model_validate(t) for t in tags]
