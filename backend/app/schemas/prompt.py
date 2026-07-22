"""Prompt request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Complexity, PromptStatus, PromptType
from app.schemas.asset import AssetRead
from app.schemas.tag import TagRead


# --- Author summary (embedded) ----------------------------------------------
class PromptAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None
    full_name: str | None
    avatar_url: str | None


class PromptCategoryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


class PromptComponentRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


# --- Version ----------------------------------------------------------------
class PromptVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_number: int
    title: str
    content: str
    change_summary: str | None
    author_id: uuid.UUID | None
    created_at: datetime


class VersionCreate(BaseModel):
    content: str = Field(min_length=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    change_summary: str | None = Field(default=None, max_length=500)


# --- Prompt create / update -------------------------------------------------
class PromptBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    prompt_type: PromptType = PromptType.UI
    complexity: Complexity = Complexity.INTERMEDIATE
    framework: str | None = Field(default=None, max_length=60)
    language: str | None = Field(default=None, max_length=60)
    ai_model: str | None = Field(default=None, max_length=60)
    estimated_tokens: int | None = Field(default=None, ge=0)
    expected_output: str | None = None
    actual_output: str | None = None
    demo_url: str | None = Field(default=None, max_length=500)
    repository_url: str | None = Field(default=None, max_length=500)
    documentation_url: str | None = Field(default=None, max_length=500)


class PromptCreate(PromptBase):
    content: str = Field(min_length=1)
    status: PromptStatus = PromptStatus.PUBLISHED
    category_id: uuid.UUID | None = None
    component_id: uuid.UUID | None = None
    tags: list[str] = Field(default_factory=list, max_length=20)


class PromptUpdate(BaseModel):
    """Metadata-only update — does not create a new version."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    prompt_type: PromptType | None = None
    complexity: Complexity | None = None
    status: PromptStatus | None = None
    framework: str | None = Field(default=None, max_length=60)
    language: str | None = Field(default=None, max_length=60)
    ai_model: str | None = Field(default=None, max_length=60)
    estimated_tokens: int | None = Field(default=None, ge=0)
    expected_output: str | None = None
    actual_output: str | None = None
    demo_url: str | None = Field(default=None, max_length=500)
    repository_url: str | None = Field(default=None, max_length=500)
    documentation_url: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    component_id: uuid.UUID | None = None
    tags: list[str] | None = Field(default=None, max_length=20)


# --- Prompt read ------------------------------------------------------------
class PromptSummary(BaseModel):
    """Lightweight shape for list/grid views (no full content bodies)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    description: str | None
    prompt_type: PromptType
    complexity: Complexity
    status: PromptStatus
    framework: str | None
    language: str | None
    ai_model: str | None
    current_version: int
    views_count: int
    copies_count: int
    likes_count: int
    forks_count: int
    rating_avg: float = 0
    rating_count: int = 0
    author: PromptAuthor
    category: PromptCategoryRef | None
    tags: list[TagRead]
    created_at: datetime
    updated_at: datetime


class PromptDetail(PromptSummary):
    """Full detail including content and reference material."""

    content: str
    estimated_tokens: int | None
    expected_output: str | None
    actual_output: str | None
    demo_url: str | None
    repository_url: str | None
    documentation_url: str | None
    forked_from_id: uuid.UUID | None
    component: PromptComponentRef | None
    assets: list[AssetRead]
    is_liked: bool = False
    is_bookmarked: bool = False
    my_rating: int | None = None


class RatingCreate(BaseModel):
    stars: int = Field(ge=1, le=5, description="1-5 star rating")


class RatingResult(BaseModel):
    rating_avg: float
    rating_count: int
    my_rating: int | None = None


class PromptContent(BaseModel):
    """Returned by the copy endpoint."""

    id: uuid.UUID
    content: str
    copies_count: int
