"""Detect contract format by content."""

from __future__ import annotations

from typing import Any, Literal

Format = Literal["openapi", "jsonschema"]


class AmbiguousFormatError(ValueError):
    """Raised when a doc looks like both formats or neither."""


def detect(doc: dict[str, Any]) -> Format:
    """Return the contract format implied by a parsed mapping.

    Detection rules (per blueprint/contracts/README.md):
      - top-level `openapi:` → OpenAPI 3.1
      - `$schema` (2020-12), or top-level `type`/`properties`/`$defs` → JSON Schema
      - both / neither → AmbiguousFormatError
    """
    has_openapi = "openapi" in doc
    has_jsonschema = (
        "$schema" in doc
        or "type" in doc
        or "properties" in doc
        or "$defs" in doc
    )

    if has_openapi and has_jsonschema:
        raise AmbiguousFormatError(
            "document has both `openapi:` and JSON Schema markers; pick one"
        )
    if has_openapi:
        return "openapi"
    if has_jsonschema:
        return "jsonschema"
    raise AmbiguousFormatError(
        "document has no `openapi:`, `$schema`, `type`, `properties`, or `$defs` "
        "at the top level — cannot determine format"
    )
