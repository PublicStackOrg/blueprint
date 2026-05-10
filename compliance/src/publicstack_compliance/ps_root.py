"""Find the Public Service root by walking up for BLUEPRINT_VERSION."""

from __future__ import annotations

from pathlib import Path


def find_public_service_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / "BLUEPRINT_VERSION").is_file():
            return d
    raise FileNotFoundError(
        "not inside a Public Service (no BLUEPRINT_VERSION found above CWD)"
    )
