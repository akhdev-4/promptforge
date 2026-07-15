"""Collection models — user-curated, shareable lists of prompts."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt
    from app.models.user import User


class Collection(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author: Mapped[User] = relationship(lazy="joined")

    items: Mapped[list[CollectionItem]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionItem.position",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Collection {self.slug}>"


class CollectionItem(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (
        UniqueConstraint("collection_id", "prompt_id", name="uq_collection_prompt"),
    )

    collection_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    collection: Mapped[Collection] = relationship(back_populates="items")
    prompt: Mapped[Prompt] = relationship(lazy="joined")
