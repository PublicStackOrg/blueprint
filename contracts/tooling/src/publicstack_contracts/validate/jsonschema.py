"""JSON Schema (Draft 2020-12) contract validity check."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


def validate_jsonschema(doc: dict[str, Any]) -> list[Finding]:
    """Return a list of Findings (empty = valid)."""
    findings: list[Finding] = []

    # PublicStack-specific required metadata.
    if not doc.get("title"):
        findings.append(Finding(path="title", message="missing required `title`"))
    if not doc.get("description"):
        findings.append(Finding(path="description", message="missing required `description`"))
    if not doc.get("x-publicstack-contract-name"):
        findings.append(
            Finding(
                path="x-publicstack-contract-name",
                message="missing required PublicStack metadata `x-publicstack-contract-name`",
            )
        )
    if not doc.get("x-publicstack-contract-version"):
        findings.append(
            Finding(
                path="x-publicstack-contract-version",
                message="missing required PublicStack metadata `x-publicstack-contract-version`",
            )
        )

    # Validate the schema itself is well-formed (a meta-validation step).
    try:
        Draft202012Validator.check_schema(doc)
    except SchemaError as e:
        findings.append(Finding(path="(schema)", message=str(e)))

    return findings
