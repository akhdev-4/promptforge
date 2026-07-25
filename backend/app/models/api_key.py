"""Personal API keys for the public API (CLI / IDE plugin / integrations).

A key's plaintext is shown to the user exactly once, at creation. We persist
only a fast SHA-256 hash for lookup (keys are high-entropy random tokens, so an
unsalted digest is safe here — unlike passwords) plus a short display ``prefix``
so users can tell their keys apart. Its own table auto-creates on startup; no
ALTER to an existing table is needed.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin


class ApiKey(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # First few characters of the token (e.g. "pf_A1b2C3d4"), for identification.
    prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # SHA-256 hex digest of the full token — the only copy we keep.
    hashed_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # Space-separated scopes. Read-only for now; kept for forward compatibility.
    scopes: Mapped[str] = mapped_column(String(255), default="read", nullable=False)

    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ApiKey {self.prefix}… user={self.user_id}>"
