"""Collection schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.prompt import PromptSummary


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    is_public: bool = True


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    is_public: bool | None = None


class CollectionAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None
    full_name: str | None


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    is_public: bool
    author: CollectionAuthor
    item_count: int = 0
    created_at: datetime


class CollectionDetail(CollectionRead):
    items: list[PromptSummary]


class CollectionItemAdd(BaseModel):
    prompt_id: uuid.UUID


# --- Interactions -----------------------------------------------------------
class LikeResponse(BaseModel):
    liked: bool
    likes_count: int


class BookmarkResponse(BaseModel):
    bookmarked: bool
