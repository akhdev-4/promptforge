"""SQL-backed search provider (PostgreSQL / SQLite)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import Prompt
from app.repositories.prompt import PromptRepository
from app.search.base import SearchQuery


class SqlSearchProvider:
    """Resolves searches via the relational store.

    Uses ``LIKE``-based matching that works identically on SQLite and
    PostgreSQL. A future provider can switch to PG full-text (``tsvector``) or
    an external engine without touching callers.
    """

    async def search(
        self, session: AsyncSession, query: SearchQuery
    ) -> tuple[list[Prompt], int]:
        repo = PromptRepository(session)
        return await repo.search(
            offset=query.offset,
            limit=query.limit,
            q=query.q,
            prompt_type=query.prompt_type,
            framework=query.framework,
            language=query.language,
            ai_model=query.ai_model,
            status=query.status,
            author_id=query.author_id,
            category_ids=query.category_ids,
            tag_slugs=query.tag_slugs,
            component_id=query.component_id,
            sort=query.sort,
        )
