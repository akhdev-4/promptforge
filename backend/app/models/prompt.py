"""Prompt and PromptVersion models.

``Prompt`` is the living entity that stores the *current* snapshot for fast
reads. ``PromptVersion`` records immutable, Git-commit-style history. Metadata
edits mutate the Prompt only; content changes append a new PromptVersion and
advance ``current_version``.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.enums import Complexity, PromptStatus, PromptType
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.asset import PromptAsset
    from app.models.category import Category
    from app.models.project import Component
    from app.models.tag import Tag
    from app.models.user import User

_PROMPT_TYPE = Enum(PromptType, native_enum=False, length=20, validate_strings=True)
_COMPLEXITY = Enum(Complexity, native_enum=False, length=20, validate_strings=True)
_STATUS = Enum(PromptStatus, native_enum=False, length=20, validate_strings=True)


class Prompt(UUIDMixin, TimestampMixin, Base):
    # --- Core content (current snapshot) -------------------------------------
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Classification -------------------------------------------------------
    prompt_type: Mapped[PromptType] = mapped_column(
        _PROMPT_TYPE, default=PromptType.UI, nullable=False, index=True
    )
    complexity: Mapped[Complexity] = mapped_column(
        _COMPLEXITY, default=Complexity.INTERMEDIATE, nullable=False
    )
    status: Mapped[PromptStatus] = mapped_column(
        _STATUS, default=PromptStatus.PUBLISHED, nullable=False, index=True
    )

    # --- Tech metadata (free-form; unlimited values) --------------------------
    framework: Mapped[str | None] = mapped_column(String(60), index=True)
    language: Mapped[str | None] = mapped_column(String(60), index=True)
    ai_model: Mapped[str | None] = mapped_column(String(60), index=True)
    estimated_tokens: Mapped[int | None] = mapped_column(Integer)

    # --- Reference material ---------------------------------------------------
    expected_output: Mapped[str | None] = mapped_column(Text)
    actual_output: Mapped[str | None] = mapped_column(Text)
    demo_url: Mapped[str | None] = mapped_column(String(500))
    repository_url: Mapped[str | None] = mapped_column(String(500))
    documentation_url: Mapped[str | None] = mapped_column(String(500))

    # --- Versioning -----------------------------------------------------------
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # --- Engagement counters (denormalized for fast sorting) ------------------
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    copies_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downloads_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- Relationships --------------------------------------------------------
    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author: Mapped[User] = relationship(lazy="joined")

    forked_from_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="SET NULL"), index=True
    )

    # --- Taxonomy (M5) --------------------------------------------------------
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    category: Mapped[Category | None] = relationship(back_populates="prompts", lazy="joined")

    component_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("components.id", ondelete="SET NULL"), index=True
    )
    component: Mapped[Component | None] = relationship(back_populates="prompts", lazy="joined")

    tags: Mapped[list[Tag]] = relationship(
        secondary="prompt_tags", back_populates="prompts", lazy="selectin"
    )

    versions: Mapped[list[PromptVersion]] = relationship(
        back_populates="prompt",
        cascade="all, delete-orphan",
        order_by="PromptVersion.version_number",
    )

    assets: Mapped[list[PromptAsset]] = relationship(
        back_populates="prompt",
        cascade="all, delete-orphan",
        order_by="PromptAsset.position",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Prompt {self.slug} v{self.current_version}>"


class PromptVersion(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (
        UniqueConstraint("prompt_id", "version_number", name="uq_prompt_version_number"),
    )

    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Immutable snapshot of the prompt at this version.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(String(500))

    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    prompt: Mapped[Prompt] = relationship(back_populates="versions")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PromptVersion prompt={self.prompt_id} v{self.version_number}>"
