"""CLI unit tests: config resolution + archive extraction (no network)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from promptforge_cli.archive import extract_zip_stripped
from promptforge_cli.config import load_config, save_config


def test_config_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMPTFORGE_HOME", str(tmp_path))
    monkeypatch.delenv("PROMPTFORGE_API_URL", raising=False)
    monkeypatch.delenv("PROMPTFORGE_API_KEY", raising=False)

    save_config("https://example.com/", "pf_abc")
    cfg = load_config()
    assert cfg["api_url"] == "https://example.com"  # trailing slash stripped
    assert cfg["api_key"] == "pf_abc"


def test_env_overrides_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMPTFORGE_HOME", str(tmp_path))
    monkeypatch.delenv("PROMPTFORGE_API_URL", raising=False)
    save_config("https://file.example", "filekey")
    monkeypatch.setenv("PROMPTFORGE_API_KEY", "envkey")

    assert load_config()["api_key"] == "envkey"


def test_default_url_when_unconfigured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMPTFORGE_HOME", str(tmp_path / "empty"))
    monkeypatch.delenv("PROMPTFORGE_API_URL", raising=False)
    monkeypatch.delenv("PROMPTFORGE_API_KEY", raising=False)
    cfg = load_config()
    assert cfg["api_url"].startswith("https://")
    assert cfg["api_key"] is None


def test_extract_strips_top_folder(tmp_path: Path) -> None:
    zip_path = tmp_path / "kit.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("repo-main/README.md", "hi")
        zf.writestr("repo-main/src/app.py", "print(1)")

    target = tmp_path / "out"
    extract_zip_stripped(zip_path, target)

    assert (target / "README.md").read_text() == "hi"
    assert (target / "src" / "app.py").exists()
    assert not (target / "repo-main").exists()  # top folder stripped
