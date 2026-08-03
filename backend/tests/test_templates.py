"""Starter template (codebase-to-Project) + public manifest tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.codebase import UnsupportedRepoError, github_archive_url
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
async def test_category_filter(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/acme/store", "category": "ecommerce"},
        headers=headers,
    )
    key = await _key(client, headers)

    matched = (await client.get(f"{PUBLIC}/templates?category=ecommerce", headers=key)).json()
    row = next(r for r in matched["items"] if r["project_id"] == pid)
    assert row["category"] == "ecommerce"

    other = (await client.get(f"{PUBLIC}/templates?category=saas", headers=key)).json()
    assert all(r["project_id"] != pid for r in other["items"])


@pytest.mark.asyncio
async def test_download_requires_github_and_template(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    key = await _key(client, headers)

    # No template yet -> 404.
    assert (
        await client.get(f"{PUBLIC}/templates/{pid}/download", headers=key)
    ).status_code == 404

    # A non-GitHub repo can't be archived -> 400 (no network hit).
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://gitlab.com/acme/store"},
        headers=headers,
    )
    resp = await client.get(f"{PUBLIC}/templates/{pid}/download", headers=key)
    assert resp.status_code == 400

    # Download requires a key.
    assert (await client.get(f"{PUBLIC}/templates/{pid}/download")).status_code == 401


@pytest.mark.asyncio
async def test_web_browse_route_is_public(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://github.com/acme/store", "category": "ecommerce"},
        headers=headers,
    )

    # The site's Starter Kits page browses without an API key.
    listing = await client.get(f"{PROJECTS}/templates?category=ecommerce")
    assert listing.status_code == 200
    assert any(r["project_id"] == pid for r in listing.json()["items"])

    # Download on a non-template project 404s.
    empty = (await client.post(PROJECTS, json={"name": "Empty"}, headers=headers)).json()
    resp = await client.get(f"{PROJECTS}/{empty['id']}/template/download")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_template_previews(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    _, other = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]

    added = await client.post(
        f"{PROJECTS}/{pid}/template/previews",
        json={"url": "data:image/png;base64,abc", "caption": "Login"},
        headers=headers,
    )
    assert added.status_code == 201, added.text
    preview = added.json()
    assert preview["caption"] == "Login"
    assert preview["position"] == 0

    # Listing is public (Codebase tab reads it without auth).
    listing = await client.get(f"{PROJECTS}/{pid}/template/previews")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    # Non-owners cannot add.
    denied = await client.post(
        f"{PROJECTS}/{pid}/template/previews",
        json={"url": "data:image/png;base64,xyz"},
        headers=other,
    )
    assert denied.status_code == 403

    # Owner deletes.
    deleted = await client.delete(
        f"{PROJECTS}/{pid}/template/previews/{preview['id']}", headers=headers
    )
    assert deleted.status_code == 204
    assert (await client.get(f"{PROJECTS}/{pid}/template/previews")).json() == []


def test_github_archive_url_builder() -> None:
    expected = "https://github.com/acme/store/archive/main.zip"
    # Bare, and the shapes people paste from the browser all normalize the same.
    for url in (
        "https://github.com/acme/store",
        "https://github.com/acme/store/",
        "https://github.com/acme/store.git",
        "https://www.github.com/acme/store",
        "https://github.com/acme/store/tree/main",
        "https://github.com/acme/store/blob/main/README.md",
        "https://github.com/acme/store?tab=readme",
    ):
        assert github_archive_url(url) == expected, url

    assert (
        github_archive_url("https://github.com/acme/store", "v2")
        == "https://github.com/acme/store/archive/v2.zip"
    )
    with pytest.raises(UnsupportedRepoError):
        github_archive_url("https://gitlab.com/acme/store")
    with pytest.raises(UnsupportedRepoError):
        github_archive_url("https://github.com/acme/store", "../evil")


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


@pytest.mark.asyncio
async def test_failed_download_does_not_count(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    s = await _scaffold(client, headers)
    pid = s["project"]["id"]
    # A non-GitHub repo can't be archived, so the pull fails before counting.
    await client.put(
        f"{PROJECTS}/{pid}/template",
        json={"repo_url": "https://gitlab.com/acme/store"},
        headers=headers,
    )
    assert (await client.get(f"{PROJECTS}/{pid}/template/download")).status_code == 400

    tpl = (await client.get(f"{PROJECTS}/{pid}/template")).json()
    assert tpl["downloads_count"] == 0
