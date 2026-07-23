"""Community & trust models: comments, reports, notifications."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt
    from app.models.user import User


class PromptComment(UUIDMixin, TimestampMixin, Base):
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    author: Mapped[User] = relationship(lazy="joined")


class PromptReport(UUIDMixin, TimestampMixin, Base):
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    # open | resolved | dismissed
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)

    prompt: Mapped[Prompt] = relationship(lazy="joined")
    reporter: Mapped[User | None] = relationship(lazy="joined")


class Notification(UUIDMixin, TimestampMixin, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str] = mapped_column(String(300), nullable=False)
    link: Mapped[str | None] = mapped_column(String(300))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
