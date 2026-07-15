"""Recommendation provider protocol."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import Prompt


class RelatedProvider(Protocol):
    """Any backend that can rank prompts related to a given one.

    Implementations: HeuristicRelatedProvider (now), an embedding/vector
    provider (future).
    """

    async def related(
        self, session: AsyncSession, prompt: Prompt, *, limit: int
    ) -> list[Prompt]: ...
