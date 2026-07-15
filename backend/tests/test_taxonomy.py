"""Category tree, tags, and taxonomy-aware search tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"
CATEGORIES = "/api/v1/categories"
TAGS = "/api/v1/tags"


def _payload(**over) -> dict:
    base = {
        "title": "Sample Prompt",
        "content": "Do something useful.",
        "prompt_type": "ui",
        "complexity": "intermediate",
        "status": "published",
    }
    base.update(over)
    return base


async def _admin(client: AsyncClient) -> dict[str, str]:
    """A moderator can manage categories; promote via direct role isn't exposed,
    so we rely on the default contributor being rejected and use a moderator by
    creating one through the DB-less path: contributors can't, so we assert 403
    where needed and use a separate helper for allowed cases."""
    _, headers = await make_user(client)
    return headers


@pytest.mark.asyncio
async def test_contributor_cannot_create_category(client: AsyncClient) -> None:
    headers = await _admin(client)
    resp = await client.post(CATEGORIES, json={"name": "Authentication"}, headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_prompt_with_tags_creates_and_counts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    resp = await client.post(
        PROMPTS,
        json=_payload(title="Glass Login", tags=["React", "Glassmorphism", "react"]),
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    # Duplicate "react"/"React" collapses to one tag.
    slugs = sorted(t["slug"] for t in body["tags"])
    assert slugs == ["glassmorphism", "react"]

    # Popular tags reflect usage.
    popular = (await client.get(f"{TAGS}/popular")).json()
    by_slug = {t["slug"]: t["usage_count"] for t in popular}
    assert by_slug["react"] == 1
    assert by_slug["glassmorphism"] == 1


@pytest.mark.asyncio
async def test_search_by_tag(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await client.post(PROMPTS, json=_payload(title="A", tags=["dark-mode"]), headers=headers)
    await client.post(PROMPTS, json=_payload(title="B", tags=["light-mode"]), headers=headers)

    resp = await client.get(PROMPTS, params={"tags": "dark-mode"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "A"


@pytest.mark.asyncio
async def test_update_tags_adjusts_counts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    created = (
        await client.post(
            PROMPTS, json=_payload(tags=["one", "two"]), headers=headers
        )
    ).json()

    # Replace tags: drop "two", add "three".
    resp = await client.patch(
        f"{PROMPTS}/{created['id']}", json={"tags": ["one", "three"]}, headers=headers
    )
    assert resp.status_code == 200
    slugs = sorted(t["slug"] for t in resp.json()["tags"])
    assert slugs == ["one", "three"]

    popular = {t["slug"]: t["usage_count"] for t in (await client.get(TAGS)).json()}
    assert popular["one"] == 1
    assert popular["two"] == 0
    assert popular["three"] == 1


@pytest.mark.asyncio
async def test_category_tree_and_descendant_search(
    client: AsyncClient, db_session
) -> None:
    """Build a small category tree directly, then verify subtree search."""
    from sqlalchemy import select

    from app.models.category import Category
    from app.models.prompt import Prompt
    from app.models.user import User

    # Root -> child hierarchy.
    root = Category(name="Frontend", slug="frontend")
    db_session.add(root)
    await db_session.flush()
    child = Category(name="Auth", slug="auth", parent_id=root.id)
    db_session.add(child)
    await db_session.flush()

    _, headers = await make_user(client)
    user = (await db_session.execute(select(User).limit(1))).scalars().first()

    # A prompt in the child category.
    p = Prompt(
        title="Login in child",
        slug="login-child",
        content="x",
        author_id=user.id,
        category_id=child.id,
    )
    db_session.add(p)
    await db_session.flush()

    # Searching the ROOT category returns prompts in descendant categories.
    resp = await client.get(PROMPTS, params={"category_id": str(root.id)})
    titles = [x["title"] for x in resp.json()["items"]]
    assert "Login in child" in titles
