"""Starter template schemas (owner management + public manifest)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.project import ProjectAuthor


# --- Owner management --------------------------------------------------------
class TemplateUpsert(BaseModel):
    repo_url: str = Field(min_length=1, max_length=500, description="Public Git URL")
    stack: str | None = Field(default=None, max_length=200)
    setup_command: str | None = Field(default=None, max_length=300)
    notes: str | None = None


class TemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    repo_url: str
    stack: str | None
    setup_command: str | None
    notes: str | None
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
    stack: str | None
    repo_url: str
    prompt_count: int
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
