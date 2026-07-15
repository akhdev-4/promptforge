"""Pluggable prompt recommendations.

Callers depend only on :class:`RelatedProvider`. Today's implementation is a
heuristic (tag/category/component/type overlap + popularity). An
embedding/semantic provider can replace it later by implementing the same
protocol and switching ``get_related_provider`` — no service/API changes.
"""

from __future__ import annotations

from app.recommendations.base import RelatedProvider
from app.recommendations.heuristic import HeuristicRelatedProvider

_provider: RelatedProvider = HeuristicRelatedProvider()


def get_related_provider() -> RelatedProvider:
    return _provider


__all__ = ["RelatedProvider", "HeuristicRelatedProvider", "get_related_provider"]
