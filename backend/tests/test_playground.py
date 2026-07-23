"""Playground (prompt runner) tests — cover the zero-key demo path + templating."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.playground.base import extract_variables, render_prompt
from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


def test_extract_and_render_variables() -> None:
    content = "Write a {{tone}} tagline for {{ product }} in {{tone}} style."
    assert extract_variables(content) == ["tone", "product"]
    rendered = render_prompt(content, {"tone": "playful", "product": "PromptForge"})
    assert rendered == "Write a playful tagline for PromptForge in playful style."
    # Unknown placeholders are left intact.
    assert "{{missing}}" in render_prompt("hi {{missing}}", {})


@pytest.mark.asyncio
async def test_run_demo_mode(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "Tagline",
                "content": "Write a tagline for {{product}}.",
                "prompt_type": "other",
                "complexity": "beginner",
                "status": "published",
            },
            headers=headers,
        )
    ).json()

    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/run",
        json={"variables": {"product": "PromptForge"}},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["is_demo"] is True
    assert body["provider"] == "demo"
    # Variable was substituted into the prompt that would be sent.
    assert "PromptForge" in body["rendered_prompt"]
    assert "{{product}}" not in body["rendered_prompt"]


@pytest.mark.asyncio
async def test_run_image_mode_returns_image_url(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "Ghibli portrait",
                "content": "A {{style}} portrait in Studio Ghibli style",
                "prompt_type": "other",
                "complexity": "beginner",
                "status": "published",
            },
            headers=headers,
        )
    ).json()

    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/run",
        json={"mode": "image", "variables": {"style": "warm"}},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["provider"] == "pollinations"
    assert body["image_url"] and body["image_url"].startswith("https://image.pollinations.ai/")
    assert "warm" in body["image_url"]  # variable substituted into the image prompt
    # Slashes/newlines are stripped so the Pollinations path doesn't 404.
    assert "%2F" not in body["image_url"] and "%0A" not in body["image_url"]


@pytest.mark.asyncio
async def test_run_stream_demo(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "Stream me",
                "content": "Say hello to {{name}}",
                "prompt_type": "other",
                "complexity": "beginner",
                "status": "published",
            },
            headers=headers,
        )
    ).json()

    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/run/stream",
        json={"variables": {"name": "Ada"}},
        headers=headers,
    )
    assert resp.status_code == 200
    assert "Demo mode" in resp.text  # mock provider streamed its text
    assert "Ada" in resp.text  # variable substituted into the streamed prompt


@pytest.mark.asyncio
async def test_run_requires_auth(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "X",
                "content": "hi",
                "prompt_type": "other",
                "complexity": "beginner",
                "status": "published",
            },
            headers=headers,
        )
    ).json()
    assert (await client.post(f"{PROMPTS}/{prompt['id']}/run", json={})).status_code == 401
