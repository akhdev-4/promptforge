"""User model and role definitions."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    """Role hierarchy, ordered from least to most privileged.

    Privilege is compared via :meth:`level`, so guards can express
    "at least Moderator" without hard-coding every role.
    """

    GUEST = "guest"
    VIEWER = "viewer"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMINISTRATOR = "administrator"

    @property
    def level(self) -> int:
        return _ROLE_ORDER.index(self)

    def satisfies(self, required: UserRole) -> bool:
        return self.level >= required.level


_ROLE_ORDER: list[UserRole] = [
    UserRole.GUEST,
    UserRole.VIEWER,
    UserRole.CONTRIBUTOR,
    UserRole.MODERATOR,
    UserRole.ADMINISTRATOR,
]


class User(UUIDMixin, TimestampMixin, Base):
    # --- Identity -------------------------------------------------------------
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(120))
    hashed_password: Mapped[str | None] = mapped_column(String(255))

    # --- Authorization --------------------------------------------------------
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20, validate_strings=True),
        default=UserRole.CONTRIBUTOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- Profile (public) -----------------------------------------------------
    # Text (not String(500)) so it can also hold a small inline data: URL when a
    # user uploads a photo from their device (compressed client-side).
    avatar_url: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(String(500))

    # --- OAuth (provider secrets not required to run; slots for M-later) -------
    oauth_provider: Mapped[str | None] = mapped_column(String(20))  # google | github
    oauth_subject: Mapped[str | None] = mapped_column(String(255))

    # --- Audit ----------------------------------------------------------------
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role.value})>"
