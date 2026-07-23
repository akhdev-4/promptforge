"""Comments, reports, moderation, and notifications."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User, UserRole
from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


async def _make_prompt(client: AsyncClient, headers: dict) -> dict:
    return (
        await client.post(
            PROMPTS,
            json={
                "title": "Discussable",
                "content": "x",
                "prompt_type": "ui",
                "complexity": "beginner",
                "status": "published",
            },
            headers=headers,
        )
    ).json()


async def _elevate(db_session, user_id: str, role: UserRole) -> None:
    user = (
        await db_session.execute(select(User).where(User.id == uuid.UUID(user_id)))
    ).scalar_one()
    user.role = role
    db_session.add(user)
    await db_session.flush()


@pytest.mark.asyncio
async def test_comment_flow_and_notifies_author(client: AsyncClient) -> None:
    author, a_headers = await make_user(client)
    prompt = await _make_prompt(client, a_headers)
    _, b_headers = await make_user(client)

    # B comments on A's prompt.
    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/comments", json={"body": "Nice one!"}, headers=b_headers
    )
    assert resp.status_code == 201, resp.text
    comment = resp.json()
    assert comment["body"] == "Nice one!"

    # It's listed.
    listed = (await client.get(f"{PROMPTS}/{prompt['id']}/comments")).json()
    assert any(c["id"] == comment["id"] for c in listed)

    # Author A got notified.
    count = (await client.get("/api/v1/users/me/notifications/unread-count", headers=a_headers)).json()
    assert count["unread"] == 1
    notes = (await client.get("/api/v1/users/me/notifications", headers=a_headers)).json()
    assert notes[0]["type"] == "comment"

    # A (not the comment author, not a moderator) cannot delete B's comment.
    assert (
        await client.delete(f"/api/v1/comments/{comment['id']}", headers=a_headers)
    ).status_code == 403
    # B can delete their own.
    assert (
        await client.delete(f"/api/v1/comments/{comment['id']}", headers=b_headers)
    ).status_code == 204


@pytest.mark.asyncio
async def test_report_and_moderation(client: AsyncClient, db_session) -> None:
    author, a_headers = await make_user(client)
    prompt = await _make_prompt(client, a_headers)
    reporter, r_headers = await make_user(client)
    mod, m_headers = await make_user(client)
    await _elevate(db_session, mod["id"], UserRole.MODERATOR)

    # Report the prompt.
    assert (
        await client.post(
            f"{PROMPTS}/{prompt['id']}/report", json={"reason": "spam"}, headers=r_headers
        )
    ).status_code == 201

    # Contributors can't view moderation; anon can't either.
    assert (await client.get("/api/v1/moderation/reports", headers=r_headers)).status_code == 403
    assert (await client.get("/api/v1/moderation/reports")).status_code == 401

    # Moderator sees the report and was notified.
    reports = (await client.get("/api/v1/moderation/reports", headers=m_headers)).json()
    assert len(reports) == 1
    assert reports[0]["prompt"]["id"] == prompt["id"]
    assert reports[0]["status"] == "open"
    notes = (await client.get("/api/v1/users/me/notifications", headers=m_headers)).json()
    assert any(n["type"] == "report" for n in notes)

    # Resolve it.
    upd = await client.patch(
        f"/api/v1/moderation/reports/{reports[0]['id']}",
        json={"status": "resolved"},
        headers=m_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_mark_notifications_read(client: AsyncClient) -> None:
    author, a_headers = await make_user(client)
    prompt = await _make_prompt(client, a_headers)
    _, b_headers = await make_user(client)
    await client.post(
        f"{PROMPTS}/{prompt['id']}/comments", json={"body": "hi"}, headers=b_headers
    )

    assert (
        await client.get("/api/v1/users/me/notifications/unread-count", headers=a_headers)
    ).json()["unread"] == 1
    assert (
        await client.post("/api/v1/users/me/notifications/read", headers=a_headers)
    ).status_code == 204
    assert (
        await client.get("/api/v1/users/me/notifications/unread-count", headers=a_headers)
    ).json()["unread"] == 0
