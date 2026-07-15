"""Category business logic: slugging, tree assembly, safe mutation."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.slug import slug_with_suffix, slugify
from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryNode, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CategoryRepository(session)

    async def _unique_slug(self, name: str) -> str:
        slug = slugify(name)
        return slug if not await self.repo.slug_exists(slug) else slug_with_suffix(name)

    async def _validate_parent(self, parent_id: uuid.UUID | None) -> None:
        if parent_id and await self.repo.get(parent_id) is None:
            raise ValidationError("Parent category does not exist")

    async def create(self, data: CategoryCreate) -> Category:
        await self._validate_parent(data.parent_id)
        return await self.repo.create(
            name=data.name,
            slug=await self._unique_slug(data.name),
            description=data.description,
            icon=data.icon,
            parent_id=data.parent_id,
            position=data.position,
        )

    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        category = await self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category not found")

        changes = data.model_dump(exclude_unset=True)
        if "parent_id" in changes:
            new_parent = changes["parent_id"]
            if new_parent == category_id:
                raise ConflictError("A category cannot be its own parent")
            await self._validate_parent(new_parent)
            # Prevent cycles: new parent must not be a descendant of this node.
            if new_parent and new_parent in set(await self.repo.descendant_ids(category_id)):
                raise ConflictError("Cannot move a category under its own descendant")
        return await self.repo.update(category, **changes)

    async def delete(self, category_id: uuid.UUID) -> None:
        category = await self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category not found")
        await self.repo.delete(category)

    async def get_tree(self) -> list[CategoryNode]:
        rows = await self.repo.all_ordered()
        nodes: dict[uuid.UUID, CategoryNode] = {
            c.id: CategoryNode.model_validate(c, from_attributes=True) for c in rows
        }
        roots: list[CategoryNode] = []
        for c in rows:
            node = nodes[c.id]
            if c.parent_id and c.parent_id in nodes:
                nodes[c.parent_id].children.append(node)
            else:
                roots.append(node)
        return roots

    async def list_flat(self) -> list[Category]:
        return await self.repo.all_ordered()
