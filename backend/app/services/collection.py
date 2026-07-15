"""Collection business logic: CRUD, membership, access control, sharing."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.slug import slug_with_suffix
from app.models.collection import Collection, CollectionItem
from app.models.prompt import Prompt
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository
from app.repositories.prompt import PromptRepository
from app.schemas.collection import CollectionCreate, CollectionUpdate


class CollectionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.collections = BaseRepository(Collection, session)
        self.items = BaseRepository(CollectionItem, session)
        self.prompts = PromptRepository(session)

    @staticmethod
    def _can_edit(collection: Collection, user: User) -> bool:
        return collection.author_id == user.id or user.role.satisfies(UserRole.MODERATOR)

    async def _get_or_404(self, collection_id: uuid.UUID) -> Collection:
        collection = await self.collections.get(collection_id)
        if collection is None:
            raise NotFoundError("Collection not found")
        return collection

    async def _item_count(self, collection_id: uuid.UUID) -> int:
        return int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(CollectionItem)
                    .where(CollectionItem.collection_id == collection_id)
                )
            ).scalar_one()
        )

    # --- Commands ------------------------------------------------------------
    async def create(self, data: CollectionCreate, user: User) -> Collection:
        return await self.collections.create(
            name=data.name,
            slug=slug_with_suffix(data.name),
            description=data.description,
            is_public=data.is_public,
            author_id=user.id,
        )

    async def update(
        self, collection_id: uuid.UUID, data: CollectionUpdate, user: User
    ) -> Collection:
        collection = await self._get_or_404(collection_id)
        if not self._can_edit(collection, user):
            raise PermissionDeniedError("You cannot edit this collection")
        return await self.collections.update(collection, **data.model_dump(exclude_unset=True))

    async def delete(self, collection_id: uuid.UUID, user: User) -> None:
        collection = await self._get_or_404(collection_id)
        if not self._can_edit(collection, user):
            raise PermissionDeniedError("You cannot delete this collection")
        await self.collections.delete(collection)

    async def add_prompt(
        self, collection_id: uuid.UUID, prompt_id: uuid.UUID, user: User
    ) -> Collection:
        collection = await self._get_or_404(collection_id)
        if not self._can_edit(collection, user):
            raise PermissionDeniedError("You cannot modify this collection")
        if await self.prompts.get(prompt_id) is None:
            raise NotFoundError("Prompt not found")
        if await self.items.get_by(collection_id=collection_id, prompt_id=prompt_id):
            raise ConflictError("Prompt is already in this collection")
        position = await self._item_count(collection_id)
        await self.items.create(
            collection_id=collection_id, prompt_id=prompt_id, position=position
        )
        return collection

    async def remove_prompt(
        self, collection_id: uuid.UUID, prompt_id: uuid.UUID, user: User
    ) -> None:
        collection = await self._get_or_404(collection_id)
        if not self._can_edit(collection, user):
            raise PermissionDeniedError("You cannot modify this collection")
        item = await self.items.get_by(collection_id=collection_id, prompt_id=prompt_id)
        if item is None:
            raise NotFoundError("Prompt is not in this collection")
        await self.items.delete(item)

    # --- Queries -------------------------------------------------------------
    async def get_detail(
        self, collection_id: uuid.UUID, user: User | None
    ) -> tuple[Collection, list[Prompt], int]:
        collection = await self._get_or_404(collection_id)
        if not collection.is_public and (user is None or not self._can_edit(collection, user)):
            raise PermissionDeniedError("This collection is private")
        stmt = (
            select(Prompt)
            .join(CollectionItem, CollectionItem.prompt_id == Prompt.id)
            .where(CollectionItem.collection_id == collection_id)
            .order_by(CollectionItem.position)
        )
        prompts = list((await self.session.execute(stmt)).unique().scalars().all())
        return collection, prompts, len(prompts)

    async def list_public(self, *, offset: int, limit: int) -> tuple[list[Collection], int]:
        total = int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(Collection)
                    .where(Collection.is_public.is_(True))
                )
            ).scalar_one()
        )
        stmt = (
            select(Collection)
            .where(Collection.is_public.is_(True))
            .order_by(Collection.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await self.session.execute(stmt)).unique().scalars().all())
        return rows, total

    async def list_for_user(self, user_id: uuid.UUID) -> list[Collection]:
        stmt = (
            select(Collection)
            .where(Collection.author_id == user_id)
            .order_by(Collection.created_at.desc())
        )
        return list((await self.session.execute(stmt)).unique().scalars().all())

    async def item_counts(self, collection_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        if not collection_ids:
            return {}
        stmt = (
            select(CollectionItem.collection_id, func.count())
            .where(CollectionItem.collection_id.in_(collection_ids))
            .group_by(CollectionItem.collection_id)
        )
        rows = await self.session.execute(stmt)
        return dict(rows.all())
