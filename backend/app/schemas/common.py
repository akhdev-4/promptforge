"""Shared schema building blocks used across every resource."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.config import settings

T = TypeVar("T")


class PageParams(BaseModel):
    """Standard pagination query parameters."""

    page: int = Field(default=1, ge=1, description="1-based page number")
    size: int = Field(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


class Page(BaseModel, Generic[T]):
    """Envelope returned by all list endpoints."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> Page[T]:
        pages = (total + params.size - 1) // params.size if params.size else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
        )


class Message(BaseModel):
    """Simple detail message response."""

    detail: str
