"""Serve a starter kit's codebase as a downloadable zip.

The kit's source of truth is a Git repo (a dedicated GitHub org, so it isn't
tied to anyone's personal account). We stream the repo's archive *through*
PromptForge so the end user pulls from our API — the underlying repo stays an
implementation detail, and pushing an update to the repo means the next
download serves the latest code automatically.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator

import httpx

# Accept only clean public GitHub repo URLs; capture owner + repo.
_GITHUB_RE = re.compile(r"^https?://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", re.I)
# A ref is a branch, tag, or SHA. Keep it to a safe charset (no slashes) so it
# can't be used for path traversal when interpolated into the archive URL.
_REF_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class UnsupportedRepoError(ValueError):
    """The repo URL isn't a downloadable public GitHub repository."""


class ArchiveUnavailableError(Exception):
    """GitHub didn't return an archive (bad ref, private, or removed)."""


def github_archive_url(repo_url: str, ref: str = "main") -> str:
    """Build the GitHub archive (zip) URL for a repo at a given ref.

    Raises ``UnsupportedRepoError`` for non-GitHub URLs or unsafe refs.
    """
    match = _GITHUB_RE.match(repo_url.strip())
    if not match:
        raise UnsupportedRepoError("Only public GitHub repository URLs can be downloaded")
    ref = (ref or "main").strip()
    if not _REF_RE.match(ref):
        raise UnsupportedRepoError("Invalid version ref")
    owner, repo = match.group(1), match.group(2)
    # This form resolves a branch, tag, or SHA and redirects to codeload.
    return f"https://github.com/{owner}/{repo}/archive/{ref}.zip"


async def open_archive(repo_url: str, ref: str = "main") -> AsyncIterator[bytes]:
    """Open the archive stream, verifying it exists before yielding bytes.

    Validates the URL/ref synchronously (raising ``UnsupportedRepoError``), then
    confirms GitHub returns 200 before streaming (raising
    ``ArchiveUnavailableError`` otherwise), so the endpoint can map failures to
    proper HTTP status codes instead of a truncated download.
    """
    url = github_archive_url(repo_url, ref)
    client = httpx.AsyncClient(follow_redirects=True, timeout=httpx.Timeout(15.0, read=120.0))
    try:
        request = client.build_request("GET", url)
        response = await client.send(request, stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        raise ArchiveUnavailableError(str(exc)) from exc
    if response.status_code != 200:
        await response.aclose()
        await client.aclose()
        raise ArchiveUnavailableError(f"GitHub returned {response.status_code}")

    async def _body() -> AsyncIterator[bytes]:
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    return _body()
