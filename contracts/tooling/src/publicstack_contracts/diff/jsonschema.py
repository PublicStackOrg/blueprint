"""JSON Schema back-compat diff entrypoint."""

from __future__ import annotations

from typing import Any

from publicstack_contracts.diff.report import Finding
from publicstack_contracts.diff.rules import diff_object


def diff_jsonschema(old: dict[str, Any], new: dict[str, Any]) -> list[Finding]:
    """Return findings for an old/new pair of JSON Schemas. Empty list = no
    breaking changes (info-severity findings may still be present)."""
    return diff_object(old, new, path="")
