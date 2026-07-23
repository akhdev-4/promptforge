"""Comment and report business logic."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.community import PromptComment, PromptReport
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.prompt import PromptRepository
from app.services.notification import NotificationService


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompts = PromptRepository(session)
        self.comments = BaseRepository(PromptComment, session)
        self.notifs = NotificationService(session)

    async def list(self, prompt_id: uuid.UUID) -> list[PromptComment]:
        stmt = (
            select(PromptComment)
            .where(PromptComment.prompt_id == prompt_id)
            .order_by(PromptComment.created_at.desc())
        )
        return list((await self.session.execute(stmt)).unique().scalars().all())

    async def create(
        self, prompt_id: uuid.UUID, user: User, body: str
    ) -> PromptComment:
        prompt = await self.prompts.get(prompt_id)
        if prompt is None:
            raise NotFoundError("Prompt not found")
        comment = await self.comments.create(
            prompt_id=prompt_id, author_id=user.id, body=body
        )
        if prompt.author_id != user.id:
            who = user.full_name or user.username or "Someone"
            await self.notifs.notify(
                prompt.author_id,
                "comment",
                f'{who} commented on your prompt "{prompt.title}"',
                f"/prompts/{prompt_id}",
            )
        return comment

    async def delete(self, comment_id: uuid.UUID, user: User) -> None:
        comment = await self.comments.get(comment_id)
        if comment is None:
            raise NotFoundError("Comment not found")
        # Only the comment's own author may delete it — no one else.
        if comment.author_id != user.id:
            raise PermissionDeniedError("You can only delete your own comment")
        await self.comments.delete(comment)


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompts = PromptRepository(session)
        self.reports = BaseRepository(PromptReport, session)
        self.notifs = NotificationService(session)

    async def create(self, prompt_id: uuid.UUID, user: User, reason: str) -> None:
        prompt = await self.prompts.get(prompt_id)
        if prompt is None:
            raise NotFoundError("Prompt not found")
        await self.reports.create(
            prompt_id=prompt_id, reporter_id=user.id, reason=reason, status="open"
        )
        await self.notifs.notify_moderators(
            "report",
            f'A prompt was reported: "{prompt.title}"',
            "/moderation",
            exclude=user.id,
        )

    async def list(self, *, status: str | None = None) -> list[PromptReport]:
        stmt = select(PromptReport).order_by(PromptReport.created_at.desc())
        if status:
            stmt = stmt.where(PromptReport.status == status)
        return list((await self.session.execute(stmt)).unique().scalars().all())

    async def update_status(self, report_id: uuid.UUID, status: str) -> PromptReport:
        report = await self.reports.get(report_id)
        if report is None:
            raise NotFoundError("Report not found")
        report.status = status
        self.session.add(report)
        await self.session.flush()
        return report
