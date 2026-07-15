"""Pluggable prompt search.

The rest of the app depends only on :class:`PromptSearchProvider`. Today the
concrete implementation is SQL-backed (``SqlSearchProvider``); a Meilisearch or
Elasticsearch provider can be dropped in later by implementing the same
protocol and switching ``get_search_provider`` — no controller/service changes.
"""

from __future__ import annotations

from app.search.base import PromptSearchProvider, SearchQuery
from app.search.sql import SqlSearchProvider

_provider: PromptSearchProvider = SqlSearchProvider()


def get_search_provider() -> PromptSearchProvider:
    return _provider


__all__ = [
    "PromptSearchProvider",
    "SearchQuery",
    "SqlSearchProvider",
    "get_search_provider",
]
