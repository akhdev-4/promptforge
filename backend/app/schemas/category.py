"""Category schemas, including a nested tree shape."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=60)
    parent_id: uuid.UUID | None = None
    position: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=60)
    parent_id: uuid.UUID | None = None
    position: int | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    parent_id: uuid.UUID | None
    position: int
    created_at: datetime


class CategoryNode(CategoryRead):
    """Category with its subtree — used by the tree endpoint."""

    children: list[CategoryNode] = []


CategoryNode.model_rebuild()
