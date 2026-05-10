"""Resolve paths to bundled templates and detect Public Service roots."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Literal

AddKind = Literal["service", "app", "contract"]


@contextmanager
def blueprint_template_dir() -> Iterator[Path]:
    """Yield a real filesystem path to the bundled `_blueprint` cookiecutter."""
    src = files("publicstack").joinpath("templates", "_blueprint")
    with as_file(src) as p:
        yield Path(p)


@contextmanager
def add_template_dir(kind: AddKind) -> Iterator[Path]:
    """Yield a real filesystem path to the bundled add-cookiecutter for `kind`."""
    src = files("publicstack").joinpath("templates", kind)
    with as_file(src) as p:
        yield Path(p)


def bundled_blueprint_version() -> str:
    """Read VERSION shipped alongside the bundled blueprint template."""
    src = files("publicstack").joinpath("templates", "_blueprint_version")
    return src.read_text(encoding="utf-8").strip()


def find_public_service_root(start: Path | None = None) -> Path:
    """Walk up from `start` (default CWD) looking for a directory containing
    BLUEPRINT_VERSION. Raises FileNotFoundError if not found."""
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / "BLUEPRINT_VERSION").is_file():
            return d
    raise FileNotFoundError("not inside a Public Service (no BLUEPRINT_VERSION found)")
