"""contract_compat check — every contract validates and no version pair has
a breaking diff.

Delegates to the publicstack_contracts library (`validate_*`, `diff_*`,
`detect`). Groups contracts by base name and runs diff between sequential
versions (v1 → v2 → ...).
"""

from __future__ import annotations

import re
from pathlib import Path

from publicstack_contracts.detect import AmbiguousFormatError, detect
from publicstack_contracts.diff import diff_jsonschema, diff_openapi
from publicstack_contracts.diff.report import has_breaking
from publicstack_contracts.load import LoadError, load
from publicstack_contracts.validate import validate_jsonschema, validate_openapi

from publicstack_compliance.findings import Finding

NAME = "contract_compat"

_NAME_VERSION = re.compile(r"^(?P<name>.+)\.v(?P<version>[0-9]+)\.(?:yaml|yml|json)$")


def _contract_files(ps_root: Path) -> list[Path]:
    out: list[Path] = []
    for sub in ("exposed", "consumed"):
        d = ps_root / "contracts" / sub
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix.lower() in {".yaml", ".yml", ".json"}:
                out.append(p)
    return out


def _key(path: Path) -> tuple[str, int] | None:
    """Return (base_name, version_int) or None if unparseable."""
    m = _NAME_VERSION.match(path.name)
    if not m:
        return None
    return m.group("name"), int(m.group("version"))


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    files = _contract_files(ps_root)

    if not files:
        findings.append(Finding(
            check=NAME, rule="CTR-004", severity="info",
            location="contracts/",
            message="no contracts under contracts/exposed/ or contracts/consumed/",
        ))
        return findings

    parsed: dict[Path, dict] = {}
    for path in files:
        try:
            doc = load(path)
        except LoadError as e:
            findings.append(Finding(
                check=NAME, rule="CTR-001", severity="breaking",
                location=str(path.relative_to(ps_root)),
                message=f"could not load: {e}",
            ))
            continue
        parsed[path] = doc

        try:
            fmt = detect(doc)
        except AmbiguousFormatError as e:
            findings.append(Finding(
                check=NAME, rule="CTR-002", severity="breaking",
                location=str(path.relative_to(ps_root)),
                message=str(e),
                suggestion=(
                    "remove either the OpenAPI marker or the JSON Schema marker"
                ),
            ))
            continue

        validator = validate_openapi if fmt == "openapi" else validate_jsonschema
        for f in validator(doc):
            findings.append(Finding(
                check=NAME, rule="CTR-001", severity="breaking",
                location=f"{path.relative_to(ps_root)}#{f.path}",
                message=f.message,
            ))

    # Group by (kind_dir, base_name) and diff sequential versions.
    groups: dict[tuple[str, str], list[tuple[int, Path]]] = {}
    for path in parsed:
        key = _key(path)
        if key is None:
            continue
        kind_dir = path.parent.name
        base, version = key
        groups.setdefault((kind_dir, base), []).append((version, path))

    for _gid, items in groups.items():
        items.sort(key=lambda x: x[0])
        for (_v_old, p_old), (_v_new, p_new) in zip(items, items[1:], strict=False):
            old_doc, new_doc = parsed[p_old], parsed[p_new]
            try:
                old_fmt = detect(old_doc)
                new_fmt = detect(new_doc)
            except AmbiguousFormatError:
                # Already reported as CTR-002; skip diffing.
                continue
            if old_fmt != new_fmt:
                findings.append(Finding(
                    check=NAME, rule="CTR-003", severity="breaking",
                    location=f"{p_old.relative_to(ps_root)} → {p_new.relative_to(ps_root)}",
                    message=f"format changed across versions: {old_fmt} → {new_fmt}",
                ))
                continue
            if old_fmt == "openapi":
                diff_findings = diff_openapi(
                    old_doc, new_doc, old_path=p_old, new_path=p_new
                )
            else:
                diff_findings = diff_jsonschema(old_doc, new_doc)
            if has_breaking(diff_findings):
                for df in diff_findings:
                    if df.severity == "breaking":
                        findings.append(Finding(
                            check=NAME, rule="CTR-003", severity="breaking",
                            location=(
                                f"{p_old.relative_to(ps_root)} → "
                                f"{p_new.relative_to(ps_root)}"
                            ),
                            message=f"[{df.rule}] {df.path}: {df.message}",
                        ))

    return findings
