"""Category endpoints: public tree/list, moderated mutations."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, require_moderator
from app.schemas.category import (
    CategoryCreate,
    CategoryNode,
    CategoryRead,
    CategoryUpdate,
)
from app.services.category import CategoryService

router = APIRouter()


@router.get("/tree", response_model=list[CategoryNode], summary="Nested category tree")
async def category_tree(db: DbSession) -> list[CategoryNode]:
    return await CategoryService(db).get_tree()


@router.get("", response_model=list[CategoryRead], summary="Flat category list")
async def list_categories(db: DbSession) -> list[CategoryRead]:
    cats = await CategoryService(db).list_flat()
    return [CategoryRead.model_validate(c) for c in cats]


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_moderator)],
    summary="Create a category (moderator+)",
)
async def create_category(data: CategoryCreate, db: DbSession) -> CategoryRead:
    category = await CategoryService(db).create(data)
    return CategoryRead.model_validate(category)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_moderator)],
    summary="Update a category (moderator+)",
)
async def update_category(
    category_id: uuid.UUID, data: CategoryUpdate, db: DbSession
) -> CategoryRead:
    category = await CategoryService(db).update(category_id, data)
    return CategoryRead.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_moderator)],
    summary="Delete a category (moderator+)",
)
async def delete_category(category_id: uuid.UUID, db: DbSession) -> None:
    await CategoryService(db).delete(category_id)
