"""Collection endpoints: CRUD, membership, sharing."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, OptionalUser
from app.schemas.collection import (
    CollectionCreate,
    CollectionDetail,
    CollectionItemAdd,
    CollectionRead,
    CollectionUpdate,
)
from app.schemas.common import Page, PageParams
from app.schemas.prompt import PromptSummary
from app.services.collection import CollectionService

router = APIRouter()


def _read(collection, item_count: int) -> CollectionRead:
    read = CollectionRead.model_validate(collection)
    read.item_count = item_count
    return read


@router.get("", response_model=Page[CollectionRead], summary="List public collections")
async def list_collections(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page[CollectionRead]:
    params = PageParams(page=page, size=size)
    service = CollectionService(db)
    items, total = await service.list_public(offset=params.offset, limit=params.limit)
    counts = await service.item_counts([c.id for c in items])
    return Page.create(
        [_read(c, counts.get(c.id, 0)) for c in items], total, params
    )


@router.post(
    "",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a collection",
)
async def create_collection(
    data: CollectionCreate, db: DbSession, user: CurrentUser
) -> CollectionRead:
    collection = await CollectionService(db).create(data, user)
    return _read(collection, 0)


@router.get("/mine", response_model=list[CollectionRead], summary="My collections")
async def my_collections(db: DbSession, user: CurrentUser) -> list[CollectionRead]:
    service = CollectionService(db)
    collections = await service.list_for_user(user.id)
    counts = await service.item_counts([c.id for c in collections])
    return [_read(c, counts.get(c.id, 0)) for c in collections]


@router.get("/{collection_id}", response_model=CollectionDetail, summary="Collection detail")
async def get_collection(
    collection_id: uuid.UUID, db: DbSession, user: OptionalUser
) -> CollectionDetail:
    collection, prompts, count = await CollectionService(db).get_detail(collection_id, user)
    base = _read(collection, count)
    return CollectionDetail(
        **base.model_dump(),
        items=[PromptSummary.model_validate(p) for p in prompts],
    )


@router.patch("/{collection_id}", response_model=CollectionRead, summary="Update a collection")
async def update_collection(
    collection_id: uuid.UUID, data: CollectionUpdate, db: DbSession, user: CurrentUser
) -> CollectionRead:
    service = CollectionService(db)
    collection = await service.update(collection_id, data, user)
    return _read(collection, await service._item_count(collection_id))


@router.delete(
    "/{collection_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a collection"
)
async def delete_collection(
    collection_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> None:
    await CollectionService(db).delete(collection_id, user)


@router.post(
    "/{collection_id}/items",
    response_model=CollectionRead,
    summary="Add a prompt to a collection",
)
async def add_item(
    collection_id: uuid.UUID, data: CollectionItemAdd, db: DbSession, user: CurrentUser
) -> CollectionRead:
    service = CollectionService(db)
    collection = await service.add_prompt(collection_id, data.prompt_id, user)
    return _read(collection, await service._item_count(collection_id))


@router.delete(
    "/{collection_id}/items/{prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a prompt from a collection",
)
async def remove_item(
    collection_id: uuid.UUID, prompt_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> None:
    await CollectionService(db).remove_prompt(collection_id, prompt_id, user)
