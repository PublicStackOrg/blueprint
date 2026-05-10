from __future__ import annotations

from pathlib import Path

import yaml

from publicstack_compliance.checks.contract_compat import run
from publicstack_compliance.findings import has_breaking


def _findings_by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


_OPENAPI_V1 = {
    "openapi": "3.1.0",
    "info": {
        "title": "citations",
        "version": "v1",
        "description": "test",
        "x-publicstack-contract-name": "citations",
        "x-publicstack-contract-version": "v1",
    },
    "paths": {},
    "components": {"schemas": {
        "Citation": {
            "type": "object",
            "required": ["id", "amount_cents"],
            "properties": {
                "id": {"type": "string"},
                "amount_cents": {"type": "integer"},
            },
        },
    }},
}

_JSONSCHEMA_V1 = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "audit_entry",
    "description": "test",
    "x-publicstack-contract-name": "audit_entry",
    "x-publicstack-contract-version": "v1",
    "type": "object",
    "required": ["id"],
    "properties": {"id": {"type": "string"}},
}


def _write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, sort_keys=False))


def test_no_contracts_emits_ctr004(ps_minimal: Path) -> None:
    # Fixture has empty contracts/ dirs.
    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "CTR-004" in by_rule
    assert not has_breaking(findings)


def test_valid_openapi_passes(ps_minimal: Path) -> None:
    _write(ps_minimal / "contracts/exposed/citations.v1.yaml", _OPENAPI_V1)
    findings = run(ps_minimal)
    assert not has_breaking(findings)


def test_invalid_contract_emits_ctr001(ps_minimal: Path) -> None:
    # Doc that fails OpenAPI structural validation: paths must be a dict.
    bad = dict(_OPENAPI_V1)
    bad["paths"] = "not a mapping"
    _write(ps_minimal / "contracts/exposed/citations.v1.yaml", bad)
    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "CTR-001" in by_rule
    assert has_breaking(findings)


def test_breaking_diff_between_v1_and_v2_emits_ctr003(ps_minimal: Path) -> None:
    _write(ps_minimal / "contracts/exposed/citations.v1.yaml", _OPENAPI_V1)
    v2 = {
        **_OPENAPI_V1,
        "info": {
            **_OPENAPI_V1["info"],
            "version": "v2",
            "x-publicstack-contract-version": "v2",
        },
        "components": {"schemas": {
            "Citation": {
                "type": "object",
                "required": ["id"],  # removed amount_cents — breaking
                "properties": {"id": {"type": "string"}},
            },
        }},
    }
    _write(ps_minimal / "contracts/exposed/citations.v2.yaml", v2)
    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "CTR-003" in by_rule
    assert has_breaking(findings)


def test_jsonschema_valid_passes(ps_minimal: Path) -> None:
    _write(ps_minimal / "contracts/exposed/audit_entry.v1.yaml", _JSONSCHEMA_V1)
    findings = run(ps_minimal)
    assert not has_breaking(findings)


def test_unparseable_yaml_emits_ctr001(ps_minimal: Path) -> None:
    bad = ps_minimal / "contracts/exposed/broken.v1.yaml"
    bad.parent.mkdir(parents=True, exist_ok=True)
    # Top-level list, not a mapping — load() rejects.
    bad.write_text("- 1\n- 2\n")
    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "CTR-001" in by_rule
