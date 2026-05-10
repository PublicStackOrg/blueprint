"""Back-compat rules JS001-JS008. Producer-perspective semantics throughout."""

from __future__ import annotations

from typing import Any

from publicstack_contracts.diff.report import Finding

# Type widenings that are NOT breaking (whitelist).
_WHITELISTED_WIDENING = {("integer", "number")}


def _norm_type(t: Any) -> set[str]:
    if t is None:
        return set()
    if isinstance(t, str):
        return {t}
    if isinstance(t, list):
        return {x for x in t if isinstance(x, str)}
    return set()


def _required_set(schema: dict[str, Any]) -> set[str]:
    req = schema.get("required") or []
    return set(req) if isinstance(req, list) else set()


def _properties(schema: dict[str, Any]) -> dict[str, Any]:
    props = schema.get("properties") or {}
    return props if isinstance(props, dict) else {}


def diff_object(old: dict[str, Any], new: dict[str, Any], path: str = "") -> list[Finding]:
    """Apply rules JS001-JS008 to a pair of subschemas. Recurses into properties,
    items, and `$defs`."""
    findings: list[Finding] = []

    old_req = _required_set(old)
    new_req = _required_set(new)
    old_props = _properties(old)
    new_props = _properties(new)

    # JS001 — removed required field
    for name in sorted(old_req - new_req - set(new_props.keys())):
        findings.append(Finding(
            rule="JS001",
            severity="breaking",
            path=f"{path}/required/{name}",
            message=f"required property '{name}' was removed",
        ))
    for name in sorted(old_req - new_req):
        if name in new_props:
            # Property still present but no longer required — additive on producer side.
            pass

    # JS002 — added required field without default
    for name in sorted(new_req - old_req):
        new_field = new_props.get(name) or {}
        if "default" not in new_field:
            findings.append(Finding(
                rule="JS002",
                severity="breaking",
                path=f"{path}/required/{name}",
                message=f"new required property '{name}' added without a default",
            ))

    # JS006 — added optional property
    for name in sorted(set(new_props) - set(old_props)):
        if name not in new_req:
            findings.append(Finding(
                rule="JS006",
                severity="info",
                path=f"{path}/properties/{name}",
                message=f"optional property '{name}' added",
            ))

    # Per-property recursion + JS003/JS004/JS005
    for name in sorted(set(old_props) & set(new_props)):
        sub_old = old_props[name] or {}
        sub_new = new_props[name] or {}
        sub_path = f"{path}/properties/{name}"
        findings.extend(diff_attributes(sub_old, sub_new, sub_path))
        findings.extend(diff_object(sub_old, sub_new, sub_path))

    # Recurse into array items.
    if isinstance(old.get("items"), dict) and isinstance(new.get("items"), dict):
        findings.extend(diff_object(old["items"], new["items"], f"{path}/items"))
        findings.extend(diff_attributes(old["items"], new["items"], f"{path}/items"))

    # Recurse into $defs.
    old_defs = old.get("$defs") or {}
    new_defs = new.get("$defs") or {}
    if isinstance(old_defs, dict) and isinstance(new_defs, dict):
        for name in sorted(set(old_defs) & set(new_defs)):
            findings.extend(diff_object(old_defs[name], new_defs[name], f"{path}/$defs/{name}"))

    return findings


def diff_attributes(old: dict[str, Any], new: dict[str, Any], path: str) -> list[Finding]:
    """JS003/JS004/JS005/JS007/JS008 for a single property's schema fragment."""
    findings: list[Finding] = []

    # JS003 — type change. Only `integer→number` is whitelisted as a widening.
    old_types = _norm_type(old.get("type"))
    new_types = _norm_type(new.get("type"))
    if old_types and new_types and old_types != new_types:
        if old_types == {"integer"} and new_types == {"number"}:
            pass  # whitelisted widening
        elif old_types - new_types:
            findings.append(Finding(
                rule="JS003",
                severity="breaking",
                path=path,
                message=f"type narrowed: {sorted(old_types)} → {sorted(new_types)}",
            ))
        elif new_types - old_types:
            findings.append(Finding(
                rule="JS003",
                severity="breaking",
                path=path,
                message=f"type widened (not whitelisted): {sorted(old_types)} → {sorted(new_types)}",
            ))

    # JS004 / JS007 — enum changes
    old_enum = old.get("enum")
    new_enum = new.get("enum")
    if isinstance(old_enum, list) and isinstance(new_enum, list):
        old_set = set(old_enum)
        new_set = set(new_enum)
        for v in sorted(old_set - new_set, key=repr):
            findings.append(Finding(
                rule="JS004",
                severity="breaking",
                path=path,
                message=f"enum value {v!r} removed",
            ))
        for v in sorted(new_set - old_set, key=repr):
            findings.append(Finding(
                rule="JS007",
                severity="info",
                path=path,
                message=f"enum value {v!r} added",
            ))

    # JS005 / JS008 — constraint tightening / loosening
    findings.extend(_diff_numeric(old, new, path, "minimum", tighten_higher=True))
    findings.extend(_diff_numeric(old, new, path, "exclusiveMinimum", tighten_higher=True))
    findings.extend(_diff_numeric(old, new, path, "maximum", tighten_higher=False))
    findings.extend(_diff_numeric(old, new, path, "exclusiveMaximum", tighten_higher=False))
    findings.extend(_diff_numeric(old, new, path, "minLength", tighten_higher=True))
    findings.extend(_diff_numeric(old, new, path, "maxLength", tighten_higher=False))
    findings.extend(_diff_numeric(old, new, path, "minItems", tighten_higher=True))
    findings.extend(_diff_numeric(old, new, path, "maxItems", tighten_higher=False))

    if "pattern" in old and "pattern" in new and old["pattern"] != new["pattern"]:
        findings.append(Finding(
            rule="JS005",
            severity="breaking",
            path=path,
            message=f"pattern changed (treated as tightening): {old['pattern']!r} → {new['pattern']!r}",
        ))

    return findings


def _diff_numeric(
    old: dict[str, Any],
    new: dict[str, Any],
    path: str,
    key: str,
    *,
    tighten_higher: bool,
) -> list[Finding]:
    """Return Findings for a single numeric constraint key.

    `tighten_higher=True` means raising the value tightens the constraint
    (e.g., `minimum`, `minLength`). False means lowering tightens.
    """
    findings: list[Finding] = []
    old_v = old.get(key)
    new_v = new.get(key)

    if old_v is None and new_v is not None:
        findings.append(Finding(
            rule="JS005",
            severity="breaking",
            path=path,
            message=f"new constraint added: {key}={new_v}",
        ))
        return findings
    if old_v is not None and new_v is None:
        findings.append(Finding(
            rule="JS008",
            severity="info",
            path=path,
            message=f"constraint removed: {key} (was {old_v})",
        ))
        return findings
    if old_v is None or new_v is None:
        return findings
    if old_v == new_v:
        return findings

    tightened = (new_v > old_v) if tighten_higher else (new_v < old_v)
    if tightened:
        findings.append(Finding(
            rule="JS005",
            severity="breaking",
            path=path,
            message=f"{key} tightened: {old_v} → {new_v}",
        ))
    else:
        findings.append(Finding(
            rule="JS008",
            severity="info",
            path=path,
            message=f"{key} loosened: {old_v} → {new_v}",
        ))
    return findings
