"""Recommendation response schemas."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.prompt import PromptSummary


class RecommendationItem(BaseModel):
    """A recommended prompt plus a short human-readable reason."""

    reason: str
    prompt: PromptSummary
