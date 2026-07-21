"""User endpoints: current profile, updates, public profiles, admin listing."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_admin
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.common import Page, PageParams
from app.schemas.prompt import PromptSummary
from app.schemas.recommendation import RecommendationItem
from app.schemas.user import UserPublic, UserRead, UserUpdate
from app.services.interaction import InteractionService
from app.services.recommendation import RecommendationService

router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get the current user")
async def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.get(
    "/me/bookmarks",
    response_model=Page[PromptSummary],
    summary="Prompts the current user has bookmarked",
)
async def my_bookmarks(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page[PromptSummary]:
    params = PageParams(page=page, size=size)
    items, total = await InteractionService(db).list_bookmarks(
        user.id, offset=params.offset, limit=params.limit
    )
    return Page.create([PromptSummary.model_validate(p) for p in items], total, params)


@router.get(
    "/me/recommendations",
    response_model=list[RecommendationItem],
    summary="Personalized prompt recommendations for the current user",
)
async def my_recommendations(
    db: DbSession,
    user: CurrentUser,
    limit: int = Query(12, ge=1, le=30),
) -> list[RecommendationItem]:
    recs = await RecommendationService(db).for_user(user.id, limit=limit)
    return [
        RecommendationItem(reason=r.reason, prompt=PromptSummary.model_validate(r.prompt))
        for r in recs
    ]


@router.patch("/me", response_model=UserRead, summary="Update the current user")
async def update_me(data: UserUpdate, user: CurrentUser, db: DbSession) -> UserRead:
    repo = UserRepository(db)
    if (
        data.username
        and data.username != user.username
        and await repo.username_exists(data.username)
    ):
        raise ConflictError("This username is already taken")
    updated = await repo.update(user, **data.model_dump(exclude_unset=True))
    return UserRead.model_validate(updated)


@router.get(
    "",
    response_model=Page[UserRead],
    dependencies=[Depends(require_admin)],
    summary="List users (admin only)",
)
async def list_users(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page[UserRead]:
    params = PageParams(page=page, size=size)
    repo = UserRepository(db)
    total = await repo.count()
    users = await repo.list(offset=params.offset, limit=params.limit, order_by=User.created_at.desc())
    return Page.create([UserRead.model_validate(u) for u in users], total, params)


@router.get("/{user_id}", response_model=UserPublic, summary="Public profile")
async def read_user(user_id: uuid.UUID, db: DbSession) -> UserPublic:
    user = await UserRepository(db).get(user_id)
    if user is None:
        raise NotFoundError("User not found")
    return UserPublic.model_validate(user)
