"""Extract a downloaded kit archive into a target directory."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


def extract_zip_stripped(zip_path: Path, target: Path) -> None:
    """Extract ``zip_path`` into ``target``, stripping a single top-level folder.

    GitHub archives wrap everything in one ``<repo>-<ref>/`` directory; we drop
    that so the code lands directly in ``target``.
    """
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_path)
        entries = list(tmp_path.iterdir())
        src = entries[0] if len(entries) == 1 and entries[0].is_dir() else tmp_path
        for item in src.iterdir():
            dest = target / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(dest))
