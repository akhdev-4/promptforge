"""Comments, reports, and moderation endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, require_moderator
from app.schemas.community import (
    CommentAuthor,
    CommentCreate,
    CommentRead,
    ReportCreate,
    ReportRead,
    ReportUpdate,
)
from app.services.community import CommentService, ReportService

router = APIRouter()


# --- Comments ---------------------------------------------------------------
@router.get(
    "/prompts/{prompt_id}/comments",
    response_model=list[CommentRead],
    tags=["comments"],
    summary="List a prompt's comments",
)
async def list_comments(prompt_id: uuid.UUID, db: DbSession) -> list[CommentRead]:
    comments = await CommentService(db).list(prompt_id)
    return [CommentRead.model_validate(c) for c in comments]


@router.post(
    "/prompts/{prompt_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
    summary="Add a comment",
)
async def add_comment(
    prompt_id: uuid.UUID, data: CommentCreate, db: DbSession, user: CurrentUser
) -> CommentRead:
    comment = await CommentService(db).create(prompt_id, user, data.body)
    # The author is the current user — build the response without a lazy load.
    return CommentRead(
        id=comment.id,
        body=comment.body,
        author=CommentAuthor.model_validate(user),
        created_at=comment.created_at,
    )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
    summary="Delete your own comment",
)
async def delete_comment(comment_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await CommentService(db).delete(comment_id, user)


# --- Reports ----------------------------------------------------------------
@router.post(
    "/prompts/{prompt_id}/report",
    status_code=status.HTTP_201_CREATED,
    tags=["reports"],
    summary="Report a prompt",
)
async def report_prompt(
    prompt_id: uuid.UUID, data: ReportCreate, db: DbSession, user: CurrentUser
) -> dict[str, bool]:
    await ReportService(db).create(prompt_id, user, data.reason)
    return {"reported": True}


# --- Moderation (moderator/admin) -------------------------------------------
@router.get(
    "/moderation/reports",
    response_model=list[ReportRead],
    dependencies=[Depends(require_moderator)],
    tags=["moderation"],
    summary="List reports",
)
async def list_reports(
    db: DbSession, status_filter: str | None = Query(None, alias="status")
) -> list[ReportRead]:
    reports = await ReportService(db).list(status=status_filter)
    return [ReportRead.model_validate(r) for r in reports]


@router.patch(
    "/moderation/reports/{report_id}",
    response_model=ReportRead,
    dependencies=[Depends(require_moderator)],
    tags=["moderation"],
    summary="Resolve or dismiss a report",
)
async def update_report(
    report_id: uuid.UUID, data: ReportUpdate, db: DbSession
) -> ReportRead:
    report = await ReportService(db).update_status(report_id, data.status)
    return ReportRead.model_validate(report)
