"""PromptAsset — previews attached to a prompt.

An asset carries either an external ``url`` (image/video/live demo) or inline
``content`` (generated HTML/code preview). This URL-or-inline shape stays valid
when object-storage uploads are added later — only the ingestion path changes.
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt


class AssetKind(str, enum.Enum):
    SCREENSHOT = "screenshot"
    IMAGE = "image"
    VIDEO = "video"
    LIVE_DEMO = "live_demo"
    GENERATED_HTML = "generated_html"
    GENERATED_CODE = "generated_code"


class PromptAsset(UUIDMixin, TimestampMixin, Base):
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[AssetKind] = mapped_column(
        Enum(AssetKind, native_enum=False, length=20, validate_strings=True),
        nullable=False,
    )
    url: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str | None] = mapped_column(Text)  # inline HTML/code
    language: Mapped[str | None] = mapped_column(String(40))  # for code previews
    caption: Mapped[str | None] = mapped_column(String(300))
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    prompt: Mapped[Prompt] = relationship(back_populates="assets")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PromptAsset {self.kind.value} prompt={self.prompt_id}>"
