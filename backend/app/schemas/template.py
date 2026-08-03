"""Starter template schemas (owner management + public manifest)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import KitCategory
from app.schemas.project import ProjectAuthor


# --- Owner management --------------------------------------------------------
class TemplateUpsert(BaseModel):
    repo_url: str = Field(min_length=1, max_length=500, description="Public Git URL")
    category: KitCategory | None = None
    stack: str | None = Field(default=None, max_length=200)
    setup_command: str | None = Field(default=None, max_length=300)
    notes: str | None = None


class PreviewCreate(BaseModel):
    # No max_length — may carry a compact inline data: URL (uploaded screenshot).
    url: str = Field(min_length=1, description="Image URL or inline data: URL")
    caption: str | None = Field(default=None, max_length=120)


class PreviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    caption: str | None
    position: int


class TemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    category: KitCategory | None
    repo_url: str
    stack: str | None
    setup_command: str | None
    notes: str | None
    downloads_count: int = 0
    created_at: datetime
    updated_at: datetime


# --- Public (key-authenticated) ---------------------------------------------
class PublicTemplateSummary(BaseModel):
    """One row in the public template catalog."""

    project_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    category: KitCategory | None
    stack: str | None
    repo_url: str
    prompt_count: int
    downloads_count: int = 0
    author: ProjectAuthor


class ManifestPrompt(BaseModel):
    id: uuid.UUID
    slug: str
    title: str


class ManifestComponent(BaseModel):
    name: str
    slug: str
    prompts: list[ManifestPrompt]


class ManifestModule(BaseModel):
    name: str
    slug: str
    components: list[ManifestComponent]


class PublicTemplateManifest(PublicTemplateSummary):
    """Everything the CLI needs to scaffold: code pointer + prompt map.

    Prompt bodies are fetched separately via ``/public/prompts/{id}`` to keep
    this response lean.
    """

    setup_command: str | None
    notes: str | None
    modules: list[ManifestModule]
