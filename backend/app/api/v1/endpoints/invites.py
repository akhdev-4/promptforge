"""Token-based team invitation endpoints (accept flow)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.team import InviteInfo, TeamDetail
from app.services.team import TeamService

router = APIRouter()


@router.get("/{token}", response_model=InviteInfo, summary="Preview an invitation")
async def invite_info(token: str, db: DbSession) -> InviteInfo:
    return await TeamService(db).get_invite_info(token)


@router.post(
    "/{token}/accept",
    response_model=TeamDetail,
    summary="Accept an invitation and join the team",
)
async def accept_invite(token: str, db: DbSession, user: CurrentUser) -> TeamDetail:
    team = await TeamService(db).accept_invite(token, user)
    return await TeamService(db).get_detail(team.id, user)
