"""Analytics aggregation queries."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.collection import Collection
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.tag import Tag
from app.models.user import User
from app.schemas.analytics import Contributor, GrowthPoint, OverviewStats, TypeCount


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _count(self, model) -> int:
        stmt = select(func.count()).select_from(model)
        return int((await self.session.execute(stmt)).scalar_one())

    async def _sum(self, column) -> int:
        stmt = select(func.coalesce(func.sum(column), 0))
        return int((await self.session.execute(stmt)).scalar_one())

    async def overview(self) -> OverviewStats:
        return OverviewStats(
            total_prompts=await self._count(Prompt),
            total_categories=await self._count(Category),
            total_collections=await self._count(Collection),
            total_projects=await self._count(Project),
            total_tags=await self._count(Tag),
            total_views=await self._sum(Prompt.views_count),
            total_copies=await self._sum(Prompt.copies_count),
            total_likes=await self._sum(Prompt.likes_count),
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

    async def growth(self, days: int = 30) -> list[GrowthPoint]:
        """New prompts per day over the last ``days`` days (dense series)."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(func.date(Prompt.created_at).label("d"), func.count().label("n"))
            .where(Prompt.created_at >= since)
            .group_by(func.date(Prompt.created_at))
        )
        rows = await self.session.execute(stmt)
        by_day = {str(r.d): r.n for r in rows}

        # Fill gaps so the chart has a continuous x-axis.
        today = datetime.now(timezone.utc).date()
        series: list[GrowthPoint] = []
        for i in range(days - 1, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            series.append(GrowthPoint(date=day, count=by_day.get(day, 0)))
        return series

    async def by_type(self) -> list[TypeCount]:
        stmt = (
            select(Prompt.prompt_type, func.count().label("n"))
            .group_by(Prompt.prompt_type)
            .order_by(func.count().desc())
        )
        rows = await self.session.execute(stmt)
        return [
            TypeCount(
                prompt_type=(r.prompt_type.value if hasattr(r.prompt_type, "value") else str(r.prompt_type)),
                count=r.n,
            )
            for r in rows
        ]
