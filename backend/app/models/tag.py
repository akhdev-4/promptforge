"""Tag model and the prompt↔tag association table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt

# Association table for the many-to-many Prompt <-> Tag relationship.
prompt_tags = Table(
    "prompt_tags",
    Base.metadata,
    Column("prompt_id", GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", GUID(), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    # Denormalized count of prompts using this tag (kept in sync by the service).
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    prompts: Mapped[list[Prompt]] = relationship(
        secondary=prompt_tags, back_populates="tags"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tag {self.slug}>"
