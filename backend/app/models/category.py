"""Category model — a self-referential tree of unlimited depth."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt


class Category(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    icon: Mapped[str | None] = mapped_column(String(60))  # optional lucide icon name
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    parent: Mapped[Category | None] = relationship(
        back_populates="children", remote_side="Category.id"
    )
    children: Mapped[list[Category]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Category.position",
    )

    prompts: Mapped[list[Prompt]] = relationship(back_populates="category")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Category {self.slug}>"
