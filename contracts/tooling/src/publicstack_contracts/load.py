"""YAML/JSON loader for contract files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class LoadError(ValueError):
    """Raised when a contract file can't be parsed."""


def load(path: Path) -> dict[str, Any]:
    """Read a YAML or JSON contract file and return the parsed mapping."""
    if not path.is_file():
        raise LoadError(f"not a file: {path}")
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    try:
        data = json.loads(text) if suffix == ".json" else yaml.safe_load(text)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise LoadError(f"failed to parse {path}: {e}") from e

    if not isinstance(data, dict):
        raise LoadError(f"expected a mapping at the top of {path}, got {type(data).__name__}")
    return data
