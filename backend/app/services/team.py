"""Team / workspace business logic + private-prompt assignment."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.core.slug import slug_with_suffix
from app.models.prompt import Prompt
from app.models.team import PromptTeam, Team, TeamMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.team import TeamCreate, TeamDetail, TeamMemberRead, TeamSummary


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.teams = BaseRepository(Team, session)
        self.members = BaseRepository(TeamMember, session)
        self.prompt_teams = BaseRepository(PromptTeam, session)

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
