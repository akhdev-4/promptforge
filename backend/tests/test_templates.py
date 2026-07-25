"""Starter template (codebase-to-Project) + public manifest tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROJECTS = "/api/v1/projects"
PROMPTS = "/api/v1/prompts"
PUBLIC = "/api/v1/public"
KEYS = "/api/v1/keys"


async def _scaffold(client: AsyncClient, headers: dict) -> dict:
    """Create project → module → component → one published prompt in it."""
    project = (
        await client.post(
            PROJECTS, json={"name": "E-commerce Store"}, headers=headers
        )
    ).json()
    module = (
        await client.post(
            f"{PROJECTS}/{project['id']}/modules",
            json={"name": "Checkout"},
            headers=headers,
        )
    ).json()
    component = (
        await client.post(
            f"{PROJECTS}/modules/{module['id']}/components",
            json={"name": "Payment Form"},
            headers=headers,
        )
    ).json()
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "Stripe Checkout Form",
                "content": "Build a Stripe checkout...",
                "status": "published",
                "component_id": component["id"],
            },
            headers=headers,
        )
    ).json()
    return {"project": project, "component": component, "prompt": prompt}


async def _key(client: AsyncClient, headers: dict) -> dict[str, str]:
    body = (await client.post(KEYS, json={"name": "cli"}, headers=headers)).json()
    return {"X-API-Key": body["key"]}


@pytest.mark.asyncio
async def test_owner_marks_project_as_template(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]

    resp = await client.put(
        f"{PROJECTS}/{pid}/template",
        json={
            "repo_url": "https://github.com/acme/store",
            "stack": "Next.js + FastAPI + Stripe",
            "setup_command": "npm install && npm run dev",
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["repo_url"] == "https://github.com/acme/store"

    got = await client.get(f"{PROJECTS}/{pid}/template")
    assert got.status_code == 200
    assert got.json()["stack"] == "Next.js + FastAPI + Stripe"


@pytest.mark.asyncio
async def test_non_owner_cannot_manage_template(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    s = await _scaffold(client, owner)
    pid = s["project"]["id"]

    resp = await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/x/y"},
        headers=other,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_public_template_catalog_and_manifest(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/acme/store", "stack": "Next.js"},
        headers=headers,
    )
    key = await _key(client, headers)

    # Requires a key.
    assert (await client.get(f"{PUBLIC}/templates")).status_code == 401

    listing = await client.get(f"{PUBLIC}/templates", headers=key)
    assert listing.status_code == 200
    row = next(r for r in listing.json()["items"] if r["project_id"] == pid)
    assert row["prompt_count"] == 1
    assert row["repo_url"] == "https://github.com/acme/store"

    manifest = await client.get(f"{PUBLIC}/templates/{pid}", headers=key)
    assert manifest.status_code == 200
    body = manifest.json()
    assert body["setup_command"] is None or isinstance(body["setup_command"], str)
    prompts = body["modules"][0]["components"][0]["prompts"]
    assert prompts[0]["id"] == s["prompt"]["id"]


@pytest.mark.asyncio
async def test_non_template_project_absent_from_catalog(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)  # never marked as a template
    key = await _key(client, headers)

    listing = (await client.get(f"{PUBLIC}/templates", headers=key)).json()
    assert all(r["project_id"] != s["project"]["id"] for r in listing["items"])

    manifest = await client.get(f"{PUBLIC}/templates/{s['project']['id']}", headers=key)
    assert manifest.status_code == 404


@pytest.mark.asyncio
async def test_manifest_excludes_private_prompts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    # Add a private (team) prompt into the same component.
    team = (await client.post("/api/v1/teams", json={"name": "Squad"}, headers=headers)).json()
    await client.post(
        PROMPTS,
        json={
            "title": "Secret Checkout Tweak",
            "content": "internal only",
            "status": "published",
            "component_id": s["component"]["id"],
            "team_id": team["id"],
        },
        headers=headers,
    )
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/acme/store"},
        headers=headers,
    )
    key = await _key(client, headers)

    manifest = (await client.get(f"{PUBLIC}/templates/{pid}", headers=key)).json()
    assert manifest["prompt_count"] == 1  # private one excluded
    titles = [p["title"] for p in manifest["modules"][0]["components"][0]["prompts"]]
    assert "Secret Checkout Tweak" not in titles


@pytest.mark.asyncio
async def test_delete_template(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/acme/store"},
        headers=headers,
    )

    resp = await client.delete(f"{PROJECTS}/{pid}/template", headers=headers)
    assert resp.status_code == 204
    assert (await client.get(f"{PROJECTS}/{pid}/template")).status_code == 404
