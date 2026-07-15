"""User↔prompt interactions: likes and bookmarks (favorites)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin


class PromptLike(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("user_id", "prompt_id", name="uq_like_user_prompt"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )


class PromptBookmark(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (
        UniqueConstraint("user_id", "prompt_id", name="uq_bookmark_user_prompt"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
