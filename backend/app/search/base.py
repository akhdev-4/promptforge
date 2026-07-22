"""Search provider protocol and query object."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromptStatus, PromptType
from app.models.prompt import Prompt
from app.repositories.prompt import SortKey


@dataclass(slots=True)
class SearchQuery:
    """Normalised, provider-agnostic prompt search request."""

    offset: int = 0
    limit: int = 20
    q: str | None = None
    prompt_type: PromptType | None = None
    framework: str | None = None
    language: str | None = None
    ai_model: str | None = None
    status: PromptStatus | None = PromptStatus.PUBLISHED
    author_id: uuid.UUID | None = None
    category_ids: list[uuid.UUID] | None = None
    exclude_category_ids: list[uuid.UUID] | None = None
    tag_slugs: list[str] | None = None
    component_id: uuid.UUID | None = None
    sort: SortKey = "newest"


class PromptSearchProvider(Protocol):
    """Any backend able to resolve a :class:`SearchQuery`.

    Implementations: SqlSearchProvider (now), MeilisearchProvider /
    ElasticsearchProvider (future).
    """

    async def search(
        self, session: AsyncSession, query: SearchQuery
    ) -> tuple[list[Prompt], int]: ...
