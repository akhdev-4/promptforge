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


INVITES = "/api/v1/invites"


@pytest.mark.asyncio
async def test_invite_by_email_accept_flow(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    invitee_me, invitee = await make_user(client)
    team = await _team(client, owner, "Squad")
    tid = team["id"]

    resp = await client.post(
        f"{TEAMS}/{tid}/invites", json={"email": invitee_me["email"]}, headers=owner
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email_sent"] is False  # no SMTP configured in tests
    token = body["link"].rsplit("/", 1)[-1]

    listed = (await client.get(f"{TEAMS}/{tid}/invites", headers=owner)).json()
    assert any(i["email"] == invitee_me["email"] for i in listed)

    info = (await client.get(f"{INVITES}/{token}")).json()
    assert info["team_name"] == "Squad"
    assert info["expired"] is False

    # The wrong user (owner) can't accept an invite addressed to someone else.
    wrong = await client.post(f"{INVITES}/{token}/accept", headers=owner)
    assert wrong.status_code == 403

    accepted = await client.post(f"{INVITES}/{token}/accept", headers=invitee)
    assert accepted.status_code == 200, accepted.text
    members = [m["username"] for m in accepted.json()["members"]]
    assert invitee_me["username"] in members

    # Re-inviting an existing member conflicts.
    dup = await client.post(
        f"{TEAMS}/{tid}/invites", json={"email": invitee_me["email"]}, headers=owner
    )
    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_only_owner_can_invite(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    team = await _team(client, owner)
    resp = await client.post(
        f"{TEAMS}/{team['id']}/invites", json={"email": "x@example.com"}, headers=other
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_revoke_invite(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    team = await _team(client, owner)
    tid = team["id"]
    invite = (
        await client.post(
            f"{TEAMS}/{tid}/invites", json={"email": "pending@example.com"}, headers=owner
        )
    ).json()
    assert len((await client.get(f"{TEAMS}/{tid}/invites", headers=owner)).json()) == 1
    deleted = await client.delete(f"{TEAMS}/{tid}/invites/{invite['id']}", headers=owner)
    assert deleted.status_code == 204
    assert (await client.get(f"{TEAMS}/{tid}/invites", headers=owner)).json() == []


@pytest.mark.asyncio
async def test_teammates_co_author_versions_of_one_prompt(client: AsyncClient) -> None:
    owner_me, owner = await make_user(client)
    mate_me, mate = await make_user(client)
    team = await _team(client, owner, "Co-authors")

    # Bring the teammate in, then make a prompt private to the team.
    await client.post(
        f"{TEAMS}/{team['id']}/members",
        json={"username": mate_me["username"]},
        headers=owner,
    )
    prompt = (
        await client.post(
            PROMPTS,
            json={
                "title": "Shared prompt",
                "content": "v1 body",
                "status": "published",
                "team_id": team["id"],
            },
            headers=owner,
        )
    ).json()

    # The teammate contributes a version to the SAME prompt (no fork).
    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/versions",
        json={"content": "v2 body", "change_summary": "Tightened the wording"},
        headers=mate,
    )
    assert resp.status_code == 201, resp.text

    versions = (await client.get(f"{PROMPTS}/{prompt['id']}/versions")).json()
    assert [v["version_number"] for v in versions] == [2, 1]
    # History now carries two different names on one prompt.
    assert versions[0]["author"]["username"] == mate_me["username"]
    assert versions[1]["author"]["username"] == owner_me["username"]


@pytest.mark.asyncio
async def test_outsiders_still_cannot_add_versions(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, stranger = await make_user(client)
    prompt = (
        await client.post(
            PROMPTS,
            json={"title": "Mine", "content": "body", "status": "published"},
            headers=owner,
        )
    ).json()

    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/versions",
        json={"content": "sneaky edit"},
        headers=stranger,
    )
    assert resp.status_code == 403
