"""Project → Module → Component hierarchy and variant tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROJECTS = "/api/v1/projects"
PROMPTS = "/api/v1/prompts"


async def _build_project(client: AsyncClient, headers: dict) -> dict:
    """Create CRM project → Authentication module → Login component."""
    project = (
        await client.post(PROJECTS, json={"name": "CRM Application"}, headers=headers)
    ).json()
    module = (
        await client.post(
            f"{PROJECTS}/{project['id']}/modules",
            json={"name": "Authentication"},
            headers=headers,
        )
    ).json()
    component = (
        await client.post(
            f"{PROJECTS}/modules/{module['id']}/components",
            json={"name": "Login"},
            headers=headers,
        )
    ).json()
    return {"project": project, "module": module, "component": component}


@pytest.mark.asyncio
async def test_create_hierarchy_and_tree(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    built = await _build_project(client, headers)

    tree = (await client.get(f"{PROJECTS}/{built['project']['id']}/tree")).json()
    assert tree["name"] == "CRM Application"
    assert len(tree["modules"]) == 1
    assert tree["modules"][0]["name"] == "Authentication"
    assert len(tree["modules"][0]["components"]) == 1
    comp = tree["modules"][0]["components"][0]
    assert comp["name"] == "Login"
    assert comp["prompt_count"] == 0


@pytest.mark.asyncio
async def test_component_holds_prompt_variants(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    built = await _build_project(client, headers)
    cid = built["component"]["id"]

    for title in ["Modern SaaS Login", "Apple Style Login", "Glass Login"]:
        resp = await client.post(
            PROMPTS,
            json={
                "title": title,
                "content": "...",
                "prompt_type": "ui",
                "complexity": "intermediate",
                "status": "published",
                "component_id": cid,
            },
            headers=headers,
        )
        assert resp.status_code == 201, resp.text

    # The tree now reports 3 variants under the Login component.
    tree = (await client.get(f"{PROJECTS}/{built['project']['id']}/tree")).json()
    assert tree["modules"][0]["components"][0]["prompt_count"] == 3

    # And they're retrievable via the component filter.
    listed = (await client.get(PROMPTS, params={"component_id": cid})).json()
    assert listed["total"] == 3
    titles = {p["title"] for p in listed["items"]}
    assert "Apple Style Login" in titles


@pytest.mark.asyncio
async def test_prompt_detail_shows_component(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    built = await _build_project(client, headers)
    p = (
        await client.post(
            PROMPTS,
            json={
                "title": "Login v1",
                "content": "x",
                "prompt_type": "ui",
                "complexity": "beginner",
                "status": "published",
                "component_id": built["component"]["id"],
            },
            headers=headers,
        )
    ).json()
    detail = (await client.get(f"{PROMPTS}/{p['id']}")).json()
    assert detail["component"]["name"] == "Login"


@pytest.mark.asyncio
async def test_invalid_component_rejected(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    import uuid

    resp = await client.post(
        PROMPTS,
        json={
            "title": "Bad",
            "content": "x",
            "prompt_type": "ui",
            "complexity": "beginner",
            "status": "published",
            "component_id": str(uuid.uuid4()),
        },
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_only_owner_manages_modules(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    built = await _build_project(client, owner)

    resp = await client.post(
        f"{PROJECTS}/{built['project']['id']}/modules",
        json={"name": "Hijack"},
        headers=other,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_project_cascades(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    built = await _build_project(client, headers)
    resp = await client.delete(f"{PROJECTS}/{built['project']['id']}", headers=headers)
    assert resp.status_code == 204
    # Tree now 404s.
    assert (await client.get(f"{PROJECTS}/{built['project']['id']}/tree")).status_code == 404
