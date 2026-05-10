"""OpenAPI 3.1 contract validity check via openapi-spec-validator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


def validate_openapi(doc: dict[str, Any]) -> list[Finding]:
    """Return a list of Findings (empty = valid). Doesn't raise; the caller
    decides exit-code shaping."""
    from openapi_spec_validator import validate
    from openapi_spec_validator.validation.exceptions import OpenAPIValidationError

    findings: list[Finding] = []

    # Hard requirement: top-level openapi field must be a 3.x string.
    version = doc.get("openapi")
    if not isinstance(version, str) or not version.startswith("3."):
        findings.append(
            Finding(path="openapi", message=f"missing or non-3.x version: {version!r}")
        )
        return findings

    # PublicStack-specific required metadata.
    info = doc.get("info") or {}
    for key in ("title", "version", "description"):
        if not info.get(key):
            findings.append(
                Finding(path=f"info.{key}", message=f"missing required metadata field info.{key}")
            )
    name = info.get("x-publicstack-contract-name")
    pversion = info.get("x-publicstack-contract-version")
    if not name:
        findings.append(
            Finding(
                path="info.x-publicstack-contract-name",
                message="missing required PublicStack metadata `info.x-publicstack-contract-name`",
            )
        )
    if not pversion:
        findings.append(
            Finding(
                path="info.x-publicstack-contract-version",
                message="missing required PublicStack metadata `info.x-publicstack-contract-version`",
            )
        )

    # Delegate full structural validation to openapi-spec-validator.
    try:
        validate(doc)
    except OpenAPIValidationError as e:
        findings.append(Finding(path="(structure)", message=str(e)))
    except Exception as e:  # noqa: BLE001 — surface any underlying parser error
        findings.append(Finding(path="(structure)", message=f"{type(e).__name__}: {e}"))

    return findings
