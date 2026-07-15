"""Line-level text diffing for version comparison."""

from __future__ import annotations

import difflib


def line_diff(old: str, new: str) -> tuple[list[dict[str, str]], int, int]:
    """Return (lines, added, removed).

    Each line is ``{"op": "equal"|"insert"|"delete", "text": ...}``. ``insert``
    marks lines present only in ``new``; ``delete`` only in ``old``.
    """
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)

    result: list[dict[str, str]] = []
    added = removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in old_lines[i1:i2]:
                result.append({"op": "equal", "text": line})
        else:
            for line in old_lines[i1:i2]:
                result.append({"op": "delete", "text": line})
                removed += 1
            for line in new_lines[j1:j2]:
                result.append({"op": "insert", "text": line})
                added += 1
    return result, added, removed
