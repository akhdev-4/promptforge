"""Team / workspace endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.prompt import PromptSummary
from app.schemas.team import AddMember, TeamCreate, TeamDetail, TeamSummary
from app.services.team import TeamService

router = APIRouter()


@router.get("", response_model=list[TeamSummary], summary="My teams")
async def my_teams(db: DbSession, user: CurrentUser) -> list[TeamSummary]:
    return await TeamService(db).list_my_teams(user)


@router.post(
    "",
    response_model=TeamDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a team",
)
async def create_team(data: TeamCreate, db: DbSession, user: CurrentUser) -> TeamDetail:
    team = await TeamService(db).create(user, data)
    return await TeamService(db).get_detail(team.id, user)


@router.get("/{team_id}", response_model=TeamDetail, summary="Team detail (members only)")
async def team_detail(team_id: uuid.UUID, db: DbSession, user: CurrentUser) -> TeamDetail:
    return await TeamService(db).get_detail(team_id, user)


@router.post(
    "/{team_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Add a member by username (owner only)",
)
async def add_member(
    team_id: uuid.UUID, data: AddMember, db: DbSession, user: CurrentUser
) -> dict[str, bool]:
    await TeamService(db).add_member(team_id, user, data.username)
    return {"added": True}


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member (owner only)",
)
async def remove_member(
    team_id: uuid.UUID, user_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> None:
    await TeamService(db).remove_member(team_id, user, user_id)


@router.get(
    "/{team_id}/prompts",
    response_model=list[PromptSummary],
    summary="Prompts private to this team (members only)",
)
async def team_prompts(
    team_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> list[PromptSummary]:
    prompts = await TeamService(db).team_prompts(team_id, user)
    return [PromptSummary.model_validate(p) for p in prompts]
