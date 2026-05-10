"""Slug validation and derivation."""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[a-z][a-z0-9_-]{1,49}$")
_PYPKG_RE = re.compile(r"^[a-z][a-z0-9_]{1,49}$")


def is_valid_slug(s: str) -> bool:
    return bool(_SLUG_RE.match(s))


def is_valid_python_package(s: str) -> bool:
    return bool(_PYPKG_RE.match(s))


def derive_slug(name: str) -> str:
    """Display name → slug. Lowercases, replaces whitespace and `.` with `-`."""
    s = name.strip().lower()
    s = re.sub(r"[\s.]+", "-", s)
    s = re.sub(r"[^a-z0-9_-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-_")
    return s


def derive_python_package(slug: str) -> str:
    """Slug → python package name (underscores only, no hyphens)."""
    return slug.replace("-", "_")
