"""Load/save CLI config (~/.promptforge/config.json), with env overrides."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_API_URL = "https://promptforge.fastapicloud.dev"


def _config_dir() -> Path:
    return Path(os.environ.get("PROMPTFORGE_HOME", str(Path.home() / ".promptforge")))


def config_file() -> Path:
    return _config_dir() / "config.json"


def load_config() -> dict[str, str | None]:
    """Resolve config: file values, overridden by PROMPTFORGE_* env vars."""
    data: dict[str, str] = {}
    path = config_file()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            data = {}
    api_url = os.environ.get("PROMPTFORGE_API_URL", data.get("api_url") or DEFAULT_API_URL)
    api_key = os.environ.get("PROMPTFORGE_API_KEY", data.get("api_key"))
    return {"api_url": api_url.rstrip("/"), "api_key": api_key}


def save_config(api_url: str, api_key: str) -> Path:
    path = config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"api_url": api_url.rstrip("/"), "api_key": api_key}, indent=2),
        encoding="utf-8",
    )
    try:  # best-effort: keep the key private on POSIX
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path
