"""Analytics response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_prompts: int
    total_categories: int
    total_collections: int
    total_projects: int
    total_tags: int
    total_views: int
    total_copies: int
    total_likes: int


class Contributor(BaseModel):
    id: uuid.UUID
    username: str | None
    full_name: str | None
    prompt_count: int


class GrowthPoint(BaseModel):
    date: str
    count: int


class TypeCount(BaseModel):
    prompt_type: str
    count: int
