"""OpenAPI 3.1 back-compat diff. Prefers `oasdiff` when on PATH; falls back to
a pure-Python checker that reuses the JSON Schema rule engine over each
component schema and request/response body."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from publicstack_contracts.diff.report import Finding
from publicstack_contracts.diff.rules import diff_attributes, diff_object


def diff_openapi(
    old: dict[str, Any],
    new: dict[str, Any],
    *,
    old_path: Path | None = None,
    new_path: Path | None = None,
) -> list[Finding]:
    if shutil.which("oasdiff") and old_path and new_path:
        return _diff_via_oasdiff(old_path, new_path)
    return _diff_via_python(old, new)


def _diff_via_oasdiff(old_path: Path, new_path: Path) -> list[Finding]:
    """Invoke `oasdiff breaking <old> <new> -f json` and translate the
    structured output into Finding objects."""
    result = subprocess.run(
        ["oasdiff", "breaking", str(old_path), str(new_path), "-f", "json"],
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        # 0 = no breaking, 1 = breaking found (per oasdiff convention).
        # Anything else is a tool error; surface as a single finding so the
        # caller can decide.
        return [Finding(
            rule="OAS999",
            severity="breaking",
            path="(oasdiff)",
            message=f"oasdiff failed (rc={result.returncode}): {result.stderr.strip()}",
        )]

    findings: list[Finding] = []
    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return [Finding(
            rule="OAS999",
            severity="breaking",
            path="(oasdiff)",
            message=f"could not parse oasdiff output: {result.stdout[:200]}",
        )]

    for entry in payload or []:
        findings.append(Finding(
            rule=f"OAS-{entry.get('id', 'UNKNOWN')}",
            severity="breaking",
            path=entry.get("operation", "") or entry.get("path", ""),
            message=entry.get("text", "") or json.dumps(entry),
        ))
    return findings


def _diff_via_python(old: dict[str, Any], new: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []

    # Component schemas.
    old_components = (old.get("components") or {}).get("schemas") or {}
    new_components = (new.get("components") or {}).get("schemas") or {}
    for name in sorted(set(old_components) - set(new_components)):
        findings.append(Finding(
            rule="OAS-COMP-REMOVED",
            severity="breaking",
            path=f"#/components/schemas/{name}",
            message=f"component schema '{name}' removed",
        ))
    for name in sorted(set(old_components) & set(new_components)):
        sub_path = f"#/components/schemas/{name}"
        # Apply both: per-schema attribute rules (type/enum/constraints) AND
        # recursion into properties. Component schemas often *are* the leaf
        # type (e.g. a string enum) and need diff_attributes at the top level.
        findings.extend(diff_attributes(old_components[name], new_components[name], sub_path))
        findings.extend(diff_object(old_components[name], new_components[name], sub_path))

    # Paths × methods.
    old_paths = old.get("paths") or {}
    new_paths = new.get("paths") or {}
    for path in sorted(set(old_paths) - set(new_paths)):
        findings.append(Finding(
            rule="OAS-PATH-REMOVED",
            severity="breaking",
            path=path,
            message=f"path '{path}' removed",
        ))

    for path in sorted(set(old_paths) & set(new_paths)):
        old_path_item = old_paths[path] or {}
        new_path_item = new_paths[path] or {}
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            old_op = old_path_item.get(method)
            new_op = new_path_item.get(method)
            if old_op and not new_op:
                findings.append(Finding(
                    rule="OAS-OP-REMOVED",
                    severity="breaking",
                    path=f"{method.upper()} {path}",
                    message="operation removed",
                ))
                continue
            if not old_op or not new_op:
                continue
            findings.extend(_diff_operation(old_op, new_op, f"{method.upper()} {path}"))

    return findings


def _diff_operation(old: dict[str, Any], new: dict[str, Any], path: str) -> list[Finding]:
    findings: list[Finding] = []

    # Request body JSON schema.
    old_rb = _request_body_schema(old)
    new_rb = _request_body_schema(new)
    if old_rb and new_rb:
        findings.extend(diff_object(old_rb, new_rb, f"{path}/requestBody"))

    # Response body JSON schemas, per status code.
    old_resps = old.get("responses") or {}
    new_resps = new.get("responses") or {}
    for code in sorted(set(old_resps) & set(new_resps)):
        old_s = _response_schema(old_resps[code])
        new_s = _response_schema(new_resps[code])
        if old_s and new_s:
            findings.extend(diff_object(old_s, new_s, f"{path}/responses/{code}"))
    for code in sorted(set(old_resps) - set(new_resps)):
        findings.append(Finding(
            rule="OAS-RESP-REMOVED",
            severity="breaking",
            path=f"{path}/responses/{code}",
            message=f"response status {code} removed",
        ))

    return findings


def _request_body_schema(op: dict[str, Any]) -> dict[str, Any] | None:
    rb = op.get("requestBody") or {}
    content = rb.get("content") or {}
    j = content.get("application/json") or {}
    return j.get("schema")


def _response_schema(resp: dict[str, Any]) -> dict[str, Any] | None:
    content = resp.get("content") or {}
    j = content.get("application/json") or {}
    return j.get("schema")
