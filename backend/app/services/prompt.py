"""Prompt business logic: creation, versioning, ownership, forking."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.diffing import line_diff
from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.core.slug import slug_with_suffix
from app.models.asset import PromptAsset
from app.models.enums import PromptStatus
from app.models.project import Component
from app.models.prompt import Prompt, PromptVersion
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository
from app.repositories.category import CategoryRepository
from app.repositories.prompt import PromptRepository, PromptVersionRepository, SortKey
from app.repositories.tag import TagRepository
from app.schemas.asset import AssetCreate, DiffLine, VersionCompare, VersionSide
from app.schemas.prompt import PromptCreate, PromptUpdate, VersionCreate
from app.search import SearchQuery, get_search_provider


class PromptService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompts = PromptRepository(session)
        self.versions = PromptVersionRepository(session)
        self.tags = TagRepository(session)
        self.categories = CategoryRepository(session)
        self.assets = BaseRepository(PromptAsset, session)
        self.components = BaseRepository(Component, session)
        self.search_provider = get_search_provider()

    # --- Taxonomy helpers ----------------------------------------------------
    async def _validate_category(self, category_id: uuid.UUID | None) -> None:
        if category_id and await self.categories.get(category_id) is None:
            raise ValidationError("Category does not exist")

    async def _validate_component(self, component_id: uuid.UUID | None) -> None:
        if component_id and await self.components.get(component_id) is None:
            raise ValidationError("Component does not exist")

    async def _sync_tags(self, prompt: Prompt, names: list[str]) -> None:
        """Set a prompt's tags to ``names`` and maintain usage counters."""
        new_tags: list[Tag] = await self.tags.resolve_many(names)
        old_by_id = {t.id: t for t in prompt.tags}
        new_by_id = {t.id: t for t in new_tags}
        for tid, tag in new_by_id.items():
            if tid not in old_by_id:
                tag.usage_count += 1
        for tid, tag in old_by_id.items():
            if tid not in new_by_id:
                tag.usage_count = max(0, tag.usage_count - 1)
        prompt.tags = new_tags
        await self.session.flush()

    # --- Authorization helpers ----------------------------------------------
    @staticmethod
    def _can_edit(prompt: Prompt, user: User) -> bool:
        return prompt.author_id == user.id or user.role.satisfies(UserRole.MODERATOR)

    @staticmethod
    def _can_delete(prompt: Prompt, user: User) -> bool:
        return prompt.author_id == user.id or user.role.satisfies(UserRole.ADMINISTRATOR)

    async def _get_or_404(self, prompt_id: uuid.UUID) -> Prompt:
        prompt = await self.prompts.get(prompt_id)
        if prompt is None:
            raise NotFoundError("Prompt not found")
        return prompt

    # --- Commands ------------------------------------------------------------
    async def create(self, data: PromptCreate, author: User) -> Prompt:
        await self._validate_category(data.category_id)
        await self._validate_component(data.component_id)
        prompt = await self.prompts.create(
            title=data.title,
            slug=slug_with_suffix(data.title),
            description=data.description,
            content=data.content,
            prompt_type=data.prompt_type,
            complexity=data.complexity,
            status=data.status,
            framework=data.framework,
            language=data.language,
            ai_model=data.ai_model,
            estimated_tokens=data.estimated_tokens,
            expected_output=data.expected_output,
            actual_output=data.actual_output,
            demo_url=data.demo_url,
            repository_url=data.repository_url,
            documentation_url=data.documentation_url,
            category_id=data.category_id,
            component_id=data.component_id,
            current_version=1,
            author_id=author.id,
        )
        if data.tags:
            await self._sync_tags(prompt, data.tags)
        # Seed version 1.
        await self.versions.create(
            prompt_id=prompt.id,
            version_number=1,
            title=prompt.title,
            content=prompt.content,
            change_summary="Initial version",
            author_id=author.id,
        )
        return prompt

    async def update_metadata(
        self, prompt_id: uuid.UUID, data: PromptUpdate, user: User
    ) -> Prompt:
        prompt = await self._get_or_404(prompt_id)
        if not self._can_edit(prompt, user):
            raise PermissionDeniedError("You cannot edit this prompt")
        changes = data.model_dump(exclude_unset=True)

        # Tags are a relationship, not a scalar column — handle separately.
        tags = changes.pop("tags", None)
        if "category_id" in changes:
            await self._validate_category(changes["category_id"])
        if "component_id" in changes:
            await self._validate_component(changes["component_id"])
        if tags is not None:
            await self._sync_tags(prompt, tags)
        if changes:
            prompt = await self.prompts.update(prompt, **changes)
        return prompt

    async def add_version(
        self, prompt_id: uuid.UUID, data: VersionCreate, user: User
    ) -> tuple[Prompt, PromptVersion]:
        prompt = await self._get_or_404(prompt_id)
        if not self._can_edit(prompt, user):
            raise PermissionDeniedError("You cannot add versions to this prompt")

        next_number = prompt.current_version + 1
        new_title = data.title or prompt.title
        version = await self.versions.create(
            prompt_id=prompt.id,
            version_number=next_number,
            title=new_title,
            content=data.content,
            change_summary=data.change_summary,
            author_id=user.id,
        )
        # Advance the living snapshot to the new version.
        await self.prompts.update(
            prompt,
            title=new_title,
            content=data.content,
            current_version=next_number,
        )
        return prompt, version

    async def delete(self, prompt_id: uuid.UUID, user: User) -> None:
        prompt = await self._get_or_404(prompt_id)
        if not self._can_delete(prompt, user):
            raise PermissionDeniedError("You cannot delete this prompt")
        await self.prompts.delete(prompt)

    async def fork(self, prompt_id: uuid.UUID, user: User) -> Prompt:
        source = await self._get_or_404(prompt_id)
        fork = await self.prompts.create(
            title=source.title,
            slug=slug_with_suffix(source.title),
            description=source.description,
            content=source.content,
            prompt_type=source.prompt_type,
            complexity=source.complexity,
            status=PromptStatus.DRAFT,
            framework=source.framework,
            language=source.language,
            ai_model=source.ai_model,
            estimated_tokens=source.estimated_tokens,
            expected_output=source.expected_output,
            actual_output=source.actual_output,
            demo_url=source.demo_url,
            repository_url=source.repository_url,
            documentation_url=source.documentation_url,
            current_version=1,
            author_id=user.id,
            forked_from_id=source.id,
        )
        await self.versions.create(
            prompt_id=fork.id,
            version_number=1,
            title=fork.title,
            content=fork.content,
            change_summary=f"Forked from {source.slug}",
            author_id=user.id,
        )
        await self.prompts.increment(source, "forks_count")
        return fork

    # --- Queries -------------------------------------------------------------
    async def get_detail(self, prompt_id: uuid.UUID, *, count_view: bool = True) -> Prompt:
        prompt = await self._get_or_404(prompt_id)
        if count_view:
            await self.prompts.increment(prompt, "views_count")
        return prompt

    async def get_by_slug(self, slug: str, *, count_view: bool = True) -> Prompt:
        prompt = await self.prompts.get_by_slug(slug)
        if prompt is None:
            raise NotFoundError("Prompt not found")
        if count_view:
            await self.prompts.increment(prompt, "views_count")
        return prompt

    async def copy(self, prompt_id: uuid.UUID) -> Prompt:
        prompt = await self._get_or_404(prompt_id)
        await self.prompts.increment(prompt, "copies_count")
        return prompt

    async def list_versions(self, prompt_id: uuid.UUID) -> list[PromptVersion]:
        await self._get_or_404(prompt_id)
        return await self.versions.list_for_prompt(prompt_id)

    async def get_version(self, prompt_id: uuid.UUID, number: int) -> PromptVersion:
        await self._get_or_404(prompt_id)
        version = await self.versions.get_version(prompt_id, number)
        if version is None:
            raise NotFoundError("Version not found")
        return version

    async def compare_versions(
        self, prompt_id: uuid.UUID, from_number: int, to_number: int
    ) -> VersionCompare:
        from_v = await self.get_version(prompt_id, from_number)
        to_v = await self.get_version(prompt_id, to_number)
        lines, added, removed = line_diff(from_v.content, to_v.content)
        return VersionCompare(
            from_version=VersionSide(
                version_number=from_v.version_number,
                title=from_v.title,
                content=from_v.content,
                change_summary=from_v.change_summary,
            ),
            to_version=VersionSide(
                version_number=to_v.version_number,
                title=to_v.title,
                content=to_v.content,
                change_summary=to_v.change_summary,
            ),
            diff=[DiffLine(**line) for line in lines],
            added=added,
            removed=removed,
        )

    # --- Assets --------------------------------------------------------------
    async def add_asset(
        self, prompt_id: uuid.UUID, data: AssetCreate, user: User
    ) -> PromptAsset:
        prompt = await self._get_or_404(prompt_id)
        if not self._can_edit(prompt, user):
            raise PermissionDeniedError("You cannot add assets to this prompt")
        return await self.assets.create(
            prompt_id=prompt.id,
            kind=data.kind,
            url=data.url,
            content=data.content,
            language=data.language,
            caption=data.caption,
            position=data.position,
        )

    async def list_assets(self, prompt_id: uuid.UUID) -> list[PromptAsset]:
        await self._get_or_404(prompt_id)
        return await self.assets.list(
            prompt_id=prompt_id, order_by=PromptAsset.position, limit=200
        )

    async def delete_asset(
        self, prompt_id: uuid.UUID, asset_id: uuid.UUID, user: User
    ) -> None:
        prompt = await self._get_or_404(prompt_id)
        if not self._can_edit(prompt, user):
            raise PermissionDeniedError("You cannot modify this prompt's assets")
        asset = await self.assets.get(asset_id)
        if asset is None or asset.prompt_id != prompt_id:
            raise NotFoundError("Asset not found")
        await self.assets.delete(asset)

    async def search(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        prompt_type=None,
        framework: str | None = None,
        language: str | None = None,
        ai_model: str | None = None,
        status: PromptStatus | None = PromptStatus.PUBLISHED,
        author_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        exclude_category_id: uuid.UUID | None = None,
        component_id: uuid.UUID | None = None,
        tags: list[str] | None = None,
        sort: SortKey = "newest",
    ) -> tuple[list[Prompt], int]:
        # Filtering by a category includes its entire subtree (both include and
        # exclude expand to the category plus all its descendants).
        category_ids = (
            await self.categories.descendant_ids(category_id) if category_id else None
        )
        exclude_category_ids = (
            await self.categories.descendant_ids(exclude_category_id)
            if exclude_category_id
            else None
        )
        query = SearchQuery(
            offset=offset,
            limit=limit,
            q=q,
            prompt_type=prompt_type,
            framework=framework,
            language=language,
            ai_model=ai_model,
            status=status,
            author_id=author_id,
            category_ids=category_ids,
            exclude_category_ids=exclude_category_ids,
            tag_slugs=tags,
            component_id=component_id,
            sort=sort,
        )
        return await self.search_provider.search(self.session, query)
