"""Teams / workspaces and the prompt→team (private) assignment.

A prompt with a PromptTeam row is *private* to that team (visible only to its
members); a prompt without one is public. Keeping this in its own table avoids
altering the prompts table.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Team(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    owner_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )


class TeamMember(UUIDMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_member"),)

    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    user: Mapped[User] = relationship(lazy="joined")


class PromptTeam(UUIDMixin, TimestampMixin, Base):
    """Presence of a row makes the prompt private to `team_id`."""

    __table_args__ = (UniqueConstraint("prompt_id", name="uq_prompt_team"),)

    prompt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
