"""Stored semantic embedding for a prompt (one per prompt)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin


class PromptEmbedding(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("prompt_id", name="uq_embedding_prompt"),)

    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # JSON-encoded list[float]; small enough (~768 dims) to keep as text.
    vector: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(60), nullable=False)
