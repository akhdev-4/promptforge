"""User data access."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def search_usernames(
        self,
        q: str | None = None,
        *,
        limit: int = 10,
        exclude_id: uuid.UUID | None = None,
    ) -> list[User]:
        """Active users with a username, A→Z. Empty ``q`` lists the first page."""
        stmt = select(User).where(User.username.is_not(None), User.is_active.is_(True))
        if q:
            stmt = stmt.where(func.lower(User.username).like(f"%{q.lower()}%"))
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        stmt = stmt.order_by(func.lower(User.username)).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.lower()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by(username=username)

    async def email_exists(self, email: str) -> bool:
        return (await self.get_by_email(email)) is not None

    async def username_exists(self, username: str) -> bool:
        return (await self.get_by_username(username)) is not None
