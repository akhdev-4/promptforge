"""Prompt asset (preview) and version-compare tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


async def _create(client: AsyncClient, headers: dict) -> dict:
    resp = await client.post(
        PROMPTS,
        json={
            "title": "Preview Prompt",
            "content": "line one\nline two\nline three",
            "prompt_type": "ui",
            "complexity": "intermediate",
            "status": "published",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_add_and_list_screenshot_asset(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _create(client, headers)

    resp = await client.post(
        f"{PROMPTS}/{p['id']}/assets",
        json={"kind": "screenshot", "url": "https://cdn.test/img.png", "caption": "Home"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["kind"] == "screenshot"

    # Appears on the prompt detail and the assets list.
    detail = (await client.get(f"{PROMPTS}/{p['id']}")).json()
    assert len(detail["assets"]) == 1
    listed = (await client.get(f"{PROMPTS}/{p['id']}/assets")).json()
    assert listed[0]["url"] == "https://cdn.test/img.png"


@pytest.mark.asyncio
async def test_screenshot_requires_url(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _create(client, headers)
    resp = await client.post(
        f"{PROMPTS}/{p['id']}/assets", json={"kind": "screenshot"}, headers=headers
    )
    assert resp.status_code == 422  # validation: url required


@pytest.mark.asyncio
async def test_generated_html_requires_content(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _create(client, headers)
    ok = await client.post(
        f"{PROMPTS}/{p['id']}/assets",
        json={"kind": "generated_html", "content": "<h1>Hi</h1>"},
        headers=headers,
    )
    assert ok.status_code == 201
    bad = await client.post(
        f"{PROMPTS}/{p['id']}/assets",
        json={"kind": "generated_html", "url": "https://x"},
        headers=headers,
    )
    assert bad.status_code == 422


@pytest.mark.asyncio
async def test_non_owner_cannot_add_asset(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    p = await _create(client, owner)
    resp = await client.post(
        f"{PROMPTS}/{p['id']}/assets",
        json={"kind": "image", "url": "https://x/y.png"},
        headers=other,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_asset(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _create(client, headers)
    asset = (
        await client.post(
            f"{PROMPTS}/{p['id']}/assets",
            json={"kind": "image", "url": "https://x/y.png"},
            headers=headers,
        )
    ).json()
    resp = await client.delete(f"{PROMPTS}/{p['id']}/assets/{asset['id']}", headers=headers)
    assert resp.status_code == 204
    assert (await client.get(f"{PROMPTS}/{p['id']}/assets")).json() == []


@pytest.mark.asyncio
async def test_version_compare_diff(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _create(client, headers)  # v1: line one/two/three
    await client.post(
        f"{PROMPTS}/{p['id']}/versions",
        json={"content": "line one\nline TWO\nline three\nline four", "change_summary": "edit"},
        headers=headers,
    )

    resp = await client.get(f"{PROMPTS}/{p['id']}/versions/compare", params={"from": 1, "to": 2})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["from_version"]["version_number"] == 1
    assert body["to_version"]["version_number"] == 2
    # "line two" -> "line TWO" is one delete + one insert; "line four" is one insert.
    assert body["added"] == 2
    assert body["removed"] == 1
    ops = {line["op"] for line in body["diff"]}
    assert {"equal", "insert", "delete"} <= ops
