"""Analytics aggregation queries."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.user import User
from app.schemas.analytics import Contributor, GrowthPoint, OverviewStats, TypeCount


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _count(self, model, owner_column=None, author_id=None) -> int:
        stmt = select(func.count()).select_from(model)
        if author_id is not None and owner_column is not None:
            stmt = stmt.where(owner_column == author_id)
        return int((await self.session.execute(stmt)).scalar_one())

    async def _sum(self, column, author_id=None) -> int:
        stmt = select(func.coalesce(func.sum(column), 0))
        if author_id is not None:
            stmt = stmt.where(Prompt.author_id == author_id)
        return int((await self.session.execute(stmt)).scalar_one())

    async def overview(self, author_id: uuid.UUID | None = None) -> OverviewStats:
        """Headline numbers. Scoped to one author's own work when given."""
        return OverviewStats(
            total_prompts=await self._count(Prompt, Prompt.author_id, author_id),
            total_collections=await self._count(
                Collection, Collection.author_id, author_id
            ),
            total_projects=await self._count(Project, Project.author_id, author_id),
            total_views=await self._sum(Prompt.views_count, author_id),
            total_copies=await self._sum(Prompt.copies_count, author_id),
            total_likes=await self._sum(Prompt.likes_count, author_id),
            total_forks=await self._sum(Prompt.forks_count, author_id),
        )

    async def top_contributors(self, limit: int = 5) -> list[Contributor]:
        stmt = (
            select(
                User.id,
                User.username,
                User.full_name,
                func.count(Prompt.id).label("n"),
            )
            .join(Prompt, Prompt.author_id == User.id)
            .group_by(User.id, User.username, User.full_name)
            .order_by(func.count(Prompt.id).desc())
            .limit(limit)
        )
        rows = await self.session.execute(stmt)
        return [
            Contributor(id=r.id, username=r.username, full_name=r.full_name, prompt_count=r.n)
            for r in rows
        ]

    async def growth(
        self, days: int = 30, author_id: uuid.UUID | None = None
    ) -> list[GrowthPoint]:
        """New prompts per day over the last ``days`` days (dense series)."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(func.date(Prompt.created_at).label("d"), func.count().label("n"))
            .where(Prompt.created_at >= since)
            .group_by(func.date(Prompt.created_at))
        )
        if author_id is not None:
            stmt = stmt.where(Prompt.author_id == author_id)
        rows = await self.session.execute(stmt)
        by_day = {str(r.d): r.n for r in rows}

        # Fill gaps so the chart has a continuous x-axis.
        today = datetime.now(timezone.utc).date()
        series: list[GrowthPoint] = []
        for i in range(days - 1, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            series.append(GrowthPoint(date=day, count=by_day.get(day, 0)))
        return series

    async def by_type(self, author_id: uuid.UUID | None = None) -> list[TypeCount]:
        stmt = (
            select(Prompt.prompt_type, func.count().label("n"))
            .group_by(Prompt.prompt_type)
            .order_by(func.count().desc())
        )
        if author_id is not None:
            stmt = stmt.where(Prompt.author_id == author_id)
        rows = await self.session.execute(stmt)
        return [
            TypeCount(
                prompt_type=(r.prompt_type.value if hasattr(r.prompt_type, "value") else str(r.prompt_type)),
                count=r.n,
            )
            for r in rows
        ]
