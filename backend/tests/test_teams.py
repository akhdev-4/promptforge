"""Teams / workspaces + private prompts."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"
TEAMS = "/api/v1/teams"


async def _team(client: AsyncClient, headers: dict, name: str = "Acme") -> dict:
    return (await client.post(TEAMS, json={"name": name}, headers=headers)).json()


async def _private_prompt(client: AsyncClient, headers: dict, team_id: str) -> dict:
    return (
        await client.post(
            PROMPTS,
            json={
                "title": "Secret sauce",
                "content": "x",
                "prompt_type": "ui",
                "complexity": "beginner",
                "status": "published",
                "team_id": team_id,
            },
            headers=headers,
        )
    ).json()


@pytest.mark.asyncio
async def test_create_team_owner_is_member(client: AsyncClient) -> None:
    owner, o = await make_user(client)
    team = await _team(client, o)
    assert team["is_owner"] is True
    assert any(m["id"] == owner["id"] and m["role"] == "owner" for m in team["members"])

    mine = (await client.get(TEAMS, headers=o)).json()
    assert any(t["id"] == team["id"] and t["member_count"] == 1 for t in mine)


@pytest.mark.asyncio
async def test_membership_management_and_access(client: AsyncClient) -> None:
    owner, o = await make_user(client)
    team = await _team(client, o)
    member, m = await make_user(client)
    outsider, x = await make_user(client)

    # Non-owner can't add members.
    assert (
        await client.post(
            f"{TEAMS}/{team['id']}/members", json={"username": member["username"]}, headers=m
        )
    ).status_code == 403
    # Owner adds the member.
    assert (
        await client.post(
            f"{TEAMS}/{team['id']}/members", json={"username": member["username"]}, headers=o
        )
    ).status_code == 201

    # Members can view the team; outsiders cannot.
    assert (await client.get(f"{TEAMS}/{team['id']}", headers=m)).status_code == 200
    assert (await client.get(f"{TEAMS}/{team['id']}", headers=x)).status_code == 403


@pytest.mark.asyncio
async def test_private_prompt_is_hidden_from_non_members(client: AsyncClient) -> None:
    owner, o = await make_user(client)
    team = await _team(client, o)
    prompt = await _private_prompt(client, o, team["id"])
    assert prompt["team_id"] == team["id"]

    # Not in the public list / search.
    listed = (await client.get(PROMPTS)).json()
    assert not any(p["id"] == prompt["id"] for p in listed["items"])

    # Present on the team's own prompt list (members only).
    team_prompts = (await client.get(f"{TEAMS}/{team['id']}/prompts", headers=o)).json()
    assert any(p["id"] == prompt["id"] for p in team_prompts)

    # Detail: member 200, outsider + anonymous get 404 (existence hidden).
    _, x = await make_user(client)
    assert (await client.get(f"{PROMPTS}/{prompt['id']}", headers=o)).status_code == 200
    assert (await client.get(f"{PROMPTS}/{prompt['id']}", headers=x)).status_code == 404
    assert (await client.get(f"{PROMPTS}/{prompt['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_cannot_assign_prompt_to_foreign_team(client: AsyncClient) -> None:
    owner, o = await make_user(client)
    team = await _team(client, o)
    _, stranger = await make_user(client)
    # A non-member trying to create a prompt in that team is rejected.
    resp = await client.post(
        PROMPTS,
        json={
            "title": "Sneaky",
            "content": "x",
            "prompt_type": "ui",
            "complexity": "beginner",
            "status": "published",
            "team_id": team["id"],
        },
        headers=stranger,
    )
    assert resp.status_code == 403
