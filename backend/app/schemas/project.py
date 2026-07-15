"""Project / Module / Component schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# --- Create / update --------------------------------------------------------
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    icon: str | None = Field(default=None, max_length=60)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    icon: str | None = Field(default=None, max_length=60)


class ModuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    position: int = 0


class ModuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    position: int | None = None


class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    position: int = 0


class ComponentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    position: int | None = None


# --- Read -------------------------------------------------------------------
class ComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    position: int
    module_id: uuid.UUID


class ModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    position: int
    project_id: uuid.UUID


class ProjectAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None
    full_name: str | None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    author: ProjectAuthor
    created_at: datetime


# --- Tree (nested with counts) ----------------------------------------------
class ComponentNode(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    position: int
    prompt_count: int


class ModuleNode(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    position: int
    components: list[ComponentNode]


class ProjectTree(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    author: ProjectAuthor
    created_at: datetime
    modules: list[ModuleNode]
