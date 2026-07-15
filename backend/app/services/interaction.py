"""Like and bookmark (favorite) business logic."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.interaction import PromptBookmark, PromptLike
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository
from app.repositories.prompt import PromptRepository


class InteractionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompts = PromptRepository(session)
        self.likes = BaseRepository(PromptLike, session)
        self.bookmarks = BaseRepository(PromptBookmark, session)

    async def _prompt_or_404(self, prompt_id: uuid.UUID) -> Prompt:
        prompt = await self.prompts.get(prompt_id)
        if prompt is None:
            raise NotFoundError("Prompt not found")
        return prompt

    async def toggle_like(self, user_id: uuid.UUID, prompt_id: uuid.UUID) -> tuple[bool, int]:
        prompt = await self._prompt_or_404(prompt_id)
        existing = await self.likes.get_by(user_id=user_id, prompt_id=prompt_id)
        if existing:
            await self.likes.delete(existing)
            await self.prompts.increment(prompt, "likes_count", by=-1)
            return False, max(0, prompt.likes_count)
        await self.likes.create(user_id=user_id, prompt_id=prompt_id)
        await self.prompts.increment(prompt, "likes_count", by=1)
        return True, prompt.likes_count

    async def toggle_bookmark(self, user_id: uuid.UUID, prompt_id: uuid.UUID) -> bool:
        await self._prompt_or_404(prompt_id)
        existing = await self.bookmarks.get_by(user_id=user_id, prompt_id=prompt_id)
        if existing:
            await self.bookmarks.delete(existing)
            return False
        await self.bookmarks.create(user_id=user_id, prompt_id=prompt_id)
        return True

    async def flags(self, user_id: uuid.UUID, prompt_id: uuid.UUID) -> tuple[bool, bool]:
        liked = await self.likes.get_by(user_id=user_id, prompt_id=prompt_id) is not None
        bookmarked = (
            await self.bookmarks.get_by(user_id=user_id, prompt_id=prompt_id) is not None
        )
        return liked, bookmarked

    async def list_bookmarks(
        self, user_id: uuid.UUID, *, offset: int, limit: int
    ) -> tuple[list[Prompt], int]:
        total = int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(PromptBookmark)
                    .where(PromptBookmark.user_id == user_id)
                )
            ).scalar_one()
        )
        stmt = (
            select(Prompt)
            .join(PromptBookmark, PromptBookmark.prompt_id == Prompt.id)
            .where(PromptBookmark.user_id == user_id)
            .order_by(PromptBookmark.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await self.session.execute(stmt)).unique().scalars().all())
        return rows, total
