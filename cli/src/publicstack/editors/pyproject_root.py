"""Round-trip editor for the workspace root pyproject.toml using tomlkit."""

from __future__ import annotations

from pathlib import Path

import tomlkit
from tomlkit import inline_table, table
from tomlkit.items import Table

from publicstack.editors import AlreadyApplied


def add_path_dep(
    pyproject_path: Path,
    name: str,
    *,
    path: str,
    develop: bool = True,
) -> None:
    """Insert `[tool.poetry.dependencies.<name>]` with `path` and `develop`.
    Idempotent: raises AlreadyApplied if the dep already exists."""
    text = pyproject_path.read_text(encoding="utf-8")
    doc = tomlkit.parse(text)

    tool = doc.get("tool")
    if tool is None or "poetry" not in tool or "dependencies" not in tool["poetry"]:
        raise ValueError(
            f"{pyproject_path} has no [tool.poetry.dependencies] section"
        )

    deps = tool["poetry"]["dependencies"]
    if name in deps:
        raise AlreadyApplied(
            f"dependency '{name}' already exists in {pyproject_path}"
        )

    sub: Table = table()
    sub.add("path", path)
    sub.add("develop", develop)
    deps[name] = sub

    pyproject_path.write_text(tomlkit.dumps(doc), encoding="utf-8")


# Inline-table form retained for callers that prefer the single-line shape.
def add_path_dep_inline(
    pyproject_path: Path,
    name: str,
    *,
    path: str,
    develop: bool = True,
) -> None:
    text = pyproject_path.read_text(encoding="utf-8")
    doc = tomlkit.parse(text)
    deps = doc["tool"]["poetry"]["dependencies"]  # type: ignore[index]
    if name in deps:
        raise AlreadyApplied(
            f"dependency '{name}' already exists in {pyproject_path}"
        )
    it = inline_table()
    it.append("path", path)
    it.append("develop", develop)
    deps[name] = it
    pyproject_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
