"""Personal API key management (authenticated via the web session/JWT).

Keys minted here authenticate requests to the public API (see ``public.py``),
which is what the CLI and IDE plugin will use.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyRead
from app.services.api_key import ApiKeyService

router = APIRouter()


@router.get("", response_model=list[ApiKeyRead], summary="List my API keys")
async def list_keys(db: DbSession, user: CurrentUser) -> list[ApiKeyRead]:
    keys = await ApiKeyService(db).list_for_user(user)
    return [ApiKeyRead.model_validate(k) for k in keys]


@router.post(
    "",
    response_model=ApiKeyCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create an API key (secret shown once)",
)
async def create_key(data: ApiKeyCreate, db: DbSession, user: CurrentUser) -> ApiKeyCreated:
    key, full_key = await ApiKeyService(db).create(user, data.name, write=data.write)
    return ApiKeyCreated(**ApiKeyRead.model_validate(key).model_dump(), key=full_key)


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an API key",
)
async def revoke_key(key_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await ApiKeyService(db).revoke(user, key_id)
