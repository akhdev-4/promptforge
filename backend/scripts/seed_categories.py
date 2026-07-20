"""Seed a nested category tree and assign existing prompts to it.

Requires the demo user (demo@promptforge.io) to have a moderator+ role
(category management is gated). Idempotent: existing categories (by name) are
reused, and prompts are (re)assigned each run.

Usage:
    python scripts/seed_categories.py                 # http://localhost
    python scripts/seed_categories.py http://localhost:8000
"""

from __future__ import annotations

import sys

import httpx

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost").rstrip("/") + "/api/v1"
AUTHOR = {"email": "demo@promptforge.io", "password": "password123"}

# (parent, [children]) — parents created first, children nested under them.
TREE: list[tuple[str, list[str]]] = [
    ("Frontend", ["Authentication UI", "Dashboards", "Landing Pages", "Design Systems"]),
    ("Backend", ["APIs", "Authentication & Security", "Async & Background Jobs"]),
    ("Database", ["Schema Design", "Query Performance", "Migrations"]),
    ("DevOps", ["Docker", "CI/CD"]),
    ("Testing", []),
    # For everyday / non-developer users — AI image & photo-editing prompts.
    (
        "Creative & Media",
        ["AI Image Prompts", "Photo Editing", "Portraits & Avatars", "Social Media"],
    ),
]

# Assign a prompt to a (leaf) category when a keyword matches its title.
# First match wins; ordered most-specific first.
RULES: list[tuple[str, str]] = [
    ("Design System", "Design Systems"),
    ("Layout & UX", "Design Systems"),
    ("Micro-interactions", "Design Systems"),
    ("Login", "Authentication UI"),
    ("REST API", "APIs"),
    ("JWT Authentication", "Authentication & Security"),
    ("Background Jobs", "Async & Background Jobs"),
    ("Multi-Tenant", "Schema Design"),
    ("E-Commerce", "Schema Design"),
    ("Query Optimization", "Query Performance"),
]


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=30.0) as client:
        tok = client.post(
            "/auth/login",
            data={"username": AUTHOR["email"], "password": AUTHOR["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tok.raise_for_status()
        headers = {"Authorization": f"Bearer {tok.json()['access_token']}"}

        # Existing categories by name (idempotency).
        by_name: dict[str, str] = {
            c["name"]: c["id"] for c in client.get("/categories").json()
        }

        def ensure(name: str, parent_id: str | None) -> str:
            if name in by_name:
                return by_name[name]
            body: dict = {"name": name}
            if parent_id:
                body["parent_id"] = parent_id
            cid = client.post("/categories", json=body, headers=headers).json()["id"]
            by_name[name] = cid
            print(f"  + category: {name}")
            return cid

        print("Categories:")
        for parent, children in TREE:
            pid = ensure(parent, None)
            for child in children:
                ensure(child, pid)

        # Assign prompts to leaf categories by title keyword.
        print("\nAssigning prompts:")
        prompts = client.get("/prompts", params={"size": 100}).json()["items"]
        assigned = 0
        for p in prompts:
            target = next(
                (by_name[cat] for kw, cat in RULES if kw.lower() in p["title"].lower()),
                None,
            )
            if target:
                client.patch(
                    f"/prompts/{p['id']}", json={"category_id": target}, headers=headers
                )
                assigned += 1
                print(f"  · {p['title']}")

        print(f"\nDone. {len(by_name)} categories; {assigned} prompts assigned.")


if __name__ == "__main__":
    main()
