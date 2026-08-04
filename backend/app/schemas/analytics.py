"""Analytics response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class OverviewStats(BaseModel):
    """Headline numbers for one author's own work."""

    total_prompts: int
    total_collections: int
    total_projects: int
    total_views: int
    total_copies: int
    total_likes: int
    total_forks: int


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
