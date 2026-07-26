"""Thin HTTP client for the PromptForge public API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from .config import load_config


class ApiError(Exception):
    """A user-facing API/auth error the CLI prints cleanly."""


class Client:
    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        cfg = load_config()
        self.api_url = (api_url or str(cfg["api_url"])).rstrip("/")
        self.api_key = api_key if api_key is not None else cfg["api_key"]

    @property
    def base(self) -> str:
        return f"{self.api_url}/api/v1/public"

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ApiError("No API key configured. Run 'promptforge login' first.")
        return {"X-API-Key": self.api_key}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            resp = httpx.get(
                f"{self.base}{path}", headers=self._headers(), params=params, timeout=30.0
            )
        except httpx.HTTPError as exc:
            raise ApiError(f"Couldn't reach {self.api_url}: {exc}") from exc
        _raise_for_status(resp)
        return resp.json()

    def download(self, path: str, dest: Path) -> None:
        """Stream a binary response (the codebase zip) to ``dest``."""
        timeout = httpx.Timeout(30.0, read=300.0)
        try:
            with httpx.stream(
                "GET",
                f"{self.base}{path}",
                headers=self._headers(),
                timeout=timeout,
                follow_redirects=True,
            ) as resp:
                _raise_for_status(resp)
                with dest.open("wb") as fh:
                    for chunk in resp.iter_bytes():
                        fh.write(chunk)
        except httpx.HTTPError as exc:
            raise ApiError(f"Download failed: {exc}") from exc


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code == 401:
        raise ApiError("Invalid or revoked API key. Run 'promptforge login' again.")
    if resp.status_code == 404:
        raise ApiError("Not found.")
    if resp.status_code == 429:
        retry = resp.headers.get("Retry-After", "a bit")
        raise ApiError(f"Rate limited — try again in {retry}s.")
    if resp.status_code >= 400:
        detail = ""
        try:
            detail = resp.json().get("detail", "")
        except ValueError:
            detail = resp.text[:200]
        raise ApiError(f"Request failed ({resp.status_code}): {detail}")
