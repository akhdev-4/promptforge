"""Team / workspace business logic + private-prompt assignment."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import send_email
from app.core.email_templates import team_invite_email
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.core.slug import slug_with_suffix
from app.models.prompt import Prompt
from app.models.team import PromptTeam, Team, TeamInvite, TeamMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.team import InviteInfo, TeamCreate, TeamDetail, TeamMemberRead, TeamSummary


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.teams = BaseRepository(Team, session)
        self.members = BaseRepository(TeamMember, session)
        self.prompt_teams = BaseRepository(PromptTeam, session)
        self.invites = BaseRepository(TeamInvite, session)

    # --- helpers -------------------------------------------------------------
    async def is_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.members.get_by(team_id=team_id, user_id=user_id) is not None

    async def _team_or_404(self, team_id: uuid.UUID) -> Team:
        team = await self.teams.get(team_id)
        if team is None:
            raise NotFoundError("Team not found")
        return team

    async def _require_member(self, team_id: uuid.UUID, user: User) -> Team:
        team = await self._team_or_404(team_id)
        if not await self.is_member(team_id, user.id):
            raise PermissionDeniedError("You are not a member of this team")
        return team

    async def _require_owner(self, team_id: uuid.UUID, user: User) -> Team:
        team = await self._team_or_404(team_id)
        if team.owner_id != user.id:
            raise PermissionDeniedError("Only the team owner can do this")
        return team

    async def _member_count(self, team_id: uuid.UUID) -> int:
        return int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(TeamMember)
                    .where(TeamMember.team_id == team_id)
                )
            ).scalar_one()
        )

    # --- CRUD ----------------------------------------------------------------
    async def create(self, user: User, data: TeamCreate) -> Team:
        team = await self.teams.create(
            name=data.name,
            slug=slug_with_suffix(data.name),
            description=data.description,
            owner_id=user.id,
        )
        await self.members.create(team_id=team.id, user_id=user.id, role="owner")
        return team

    async def list_my_teams(self, user: User) -> list[TeamSummary]:
        stmt = (
            select(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .where(TeamMember.user_id == user.id)
            .order_by(Team.created_at.desc())
        )
        teams = list((await self.session.execute(stmt)).unique().scalars().all())
        out: list[TeamSummary] = []
        for team in teams:
            out.append(
                TeamSummary(
                    id=team.id,
                    name=team.name,
                    slug=team.slug,
                    description=team.description,
                    owner_id=team.owner_id,
                    created_at=team.created_at,
                    member_count=await self._member_count(team.id),
                    is_owner=team.owner_id == user.id,
                )
            )
        return out

    async def get_detail(self, team_id: uuid.UUID, user: User) -> TeamDetail:
        team = await self._require_member(team_id, user)
        rows = list(
            (
                await self.session.execute(
                    select(TeamMember).where(TeamMember.team_id == team_id)
                )
            )
            .unique()
            .scalars()
            .all()
        )
        members = [
            TeamMemberRead(
                id=m.user.id,
                username=m.user.username,
                full_name=m.user.full_name,
                avatar_url=m.user.avatar_url,
                role=m.role,
            )
            for m in rows
        ]
        return TeamDetail(
            id=team.id,
            name=team.name,
            slug=team.slug,
            description=team.description,
            owner_id=team.owner_id,
            created_at=team.created_at,
            is_owner=team.owner_id == user.id,
            members=members,
        )

    async def add_member(self, team_id: uuid.UUID, owner: User, username: str) -> None:
        await self._require_owner(team_id, owner)
        user = (
            await self.session.execute(select(User).where(User.username == username))
        ).scalar_one_or_none()
        if user is None:
            raise NotFoundError(f"No user named @{username}")
        if await self.is_member(team_id, user.id):
            raise ConflictError("That user is already a member")
        await self.members.create(team_id=team_id, user_id=user.id, role="member")

    async def remove_member(
        self, team_id: uuid.UUID, owner: User, user_id: uuid.UUID
    ) -> None:
        team = await self._require_owner(team_id, owner)
        if user_id == team.owner_id:
            raise PermissionDeniedError("The owner cannot be removed")
        member = await self.members.get_by(team_id=team_id, user_id=user_id)
        if member is None:
            raise NotFoundError("Member not found")
        await self.members.delete(member)

    # --- Invitations ---------------------------------------------------------
    async def _user_by_email(self, email: str) -> User | None:
        return (
            await self.session.execute(
                select(User).where(func.lower(User.email) == email.lower())
            )
        ).scalar_one_or_none()

    def _invite_link(self, token: str) -> str:
        return f"{settings.FRONTEND_URL.rstrip('/')}/invite/{token}"

    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        # SQLite may hand back a naive datetime; treat stored times as UTC.
        aware = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
        return aware < datetime.now(timezone.utc)

    async def create_invite(
        self, team_id: uuid.UUID, owner: User, email: str
    ) -> tuple[TeamInvite, str, bool]:
        """Invite an email to a team. Returns (invite, link, email_sent)."""
        team = await self._require_owner(team_id, owner)
        email = email.strip().lower()

        existing_user = await self._user_by_email(email)
        if existing_user and await self.is_member(team_id, existing_user.id):
            raise ConflictError("That person is already a member of this team")

        # Reuse a still-pending invite for the same email instead of duplicating.
        invite = (
            await self.session.execute(
                select(TeamInvite).where(
                    TeamInvite.team_id == team_id,
                    func.lower(TeamInvite.email) == email,
                    TeamInvite.status == "pending",
                )
            )
        ).scalar_one_or_none()
        expires = datetime.now(timezone.utc) + timedelta(
            hours=settings.TEAM_INVITE_EXPIRE_HOURS
        )
        if invite is None:
            invite = await self.invites.create(
                team_id=team_id,
                email=email,
                token=secrets.token_urlsafe(32),
                invited_by=owner.id,
                status="pending",
                expires_at=expires,
            )
        else:
            invite.expires_at = expires
            self.session.add(invite)
            await self.session.flush()

        link = self._invite_link(invite.token)
        inviter = owner.full_name or (f"@{owner.username}" if owner.username else "Someone")
        subject, text, html = team_invite_email(
            team_name=team.name,
            inviter=inviter,
            link=link,
            expires_days=max(1, settings.TEAM_INVITE_EXPIRE_HOURS // 24),
        )
        sent = await send_email(email, subject, text=text, html=html)
        return invite, link, sent

    async def list_invites(self, team_id: uuid.UUID, user: User) -> list[TeamInvite]:
        await self._require_member(team_id, user)
        stmt = (
            select(TeamInvite)
            .where(TeamInvite.team_id == team_id, TeamInvite.status == "pending")
            .order_by(TeamInvite.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke_invite(
        self, team_id: uuid.UUID, owner: User, invite_id: uuid.UUID
    ) -> None:
        await self._require_owner(team_id, owner)
        invite = await self.invites.get(invite_id)
        if invite is None or invite.team_id != team_id:
            raise NotFoundError("Invite not found")
        invite.status = "revoked"
        self.session.add(invite)
        await self.session.flush()

    async def get_invite_info(self, token: str) -> InviteInfo:
        invite = await self.invites.get_by(token=token)
        if invite is None:
            raise NotFoundError("Invite not found")
        team = await self._team_or_404(invite.team_id)
        expired = self._is_expired(invite.expires_at)
        return InviteInfo(
            team_name=team.name,
            email=invite.email,
            status=invite.status,
            expired=expired,
        )

    async def accept_invite(self, token: str, user: User) -> Team:
        invite = await self.invites.get_by(token=token)
        if invite is None:
            raise NotFoundError("Invite not found")
        if invite.status != "pending":
            raise ConflictError("This invitation is no longer valid")
        if self._is_expired(invite.expires_at):
            raise ConflictError("This invitation has expired")
        if user.email.lower() != invite.email.lower():
            raise PermissionDeniedError(
                f"This invite was sent to {invite.email}. Sign in as that user to accept."
            )
        team = await self._team_or_404(invite.team_id)
        if not await self.is_member(team.id, user.id):
            await self.members.create(team_id=team.id, user_id=user.id, role=invite.role)
        invite.status = "accepted"
        invite.accepted_at = datetime.now(timezone.utc)
        self.session.add(invite)
        await self.session.flush()
        return team

    # --- Prompts -------------------------------------------------------------
    async def team_prompts(self, team_id: uuid.UUID, user: User) -> list[Prompt]:
        await self._require_member(team_id, user)
        stmt = (
            select(Prompt)
            .join(PromptTeam, PromptTeam.prompt_id == Prompt.id)
            .where(PromptTeam.team_id == team_id)
            .order_by(Prompt.created_at.desc())
        )
        return list((await self.session.execute(stmt)).unique().scalars().all())

    async def assign_prompt(
        self, prompt_id: uuid.UUID, team_id: uuid.UUID, user: User
    ) -> None:
        """Make a prompt private to a team the user belongs to."""
        await self._require_member(team_id, user)
        existing = await self.prompt_teams.get_by(prompt_id=prompt_id)
        if existing:
            existing.team_id = team_id
            self.session.add(existing)
        else:
            await self.prompt_teams.create(prompt_id=prompt_id, team_id=team_id)
        await self.session.flush()

    async def team_of_prompt(self, prompt_id: uuid.UUID) -> uuid.UUID | None:
        row = await self.prompt_teams.get_by(prompt_id=prompt_id)
        return row.team_id if row else None
