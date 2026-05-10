from __future__ import annotations

from pathlib import Path

import yaml

from publicstack_contracts.validate.jsonschema import validate_jsonschema


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


def test_audit_entry_exemplar_valid(examples_dir: Path):
    findings = validate_jsonschema(_load(examples_dir / "audit_entry.v1.yaml"))
    assert findings == []


def test_identity_token_exemplar_valid(examples_dir: Path):
    findings = validate_jsonschema(_load(examples_dir / "identity_token.v1.yaml"))
    assert findings == []


def test_missing_metadata():
    findings = validate_jsonschema({"type": "object"})
    paths = {f.path for f in findings}
    assert "title" in paths
    assert "description" in paths
    assert "x-publicstack-contract-name" in paths
    assert "x-publicstack-contract-version" in paths


def test_invalid_schema_structure():
    # `type` must be a string or list of strings, not an int.
    findings = validate_jsonschema({
        "title": "x",
        "description": "y",
        "x-publicstack-contract-name": "x",
        "x-publicstack-contract-version": "v1",
        "type": 42,
    })
    assert any(f.path == "(schema)" for f in findings)
