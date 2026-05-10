from __future__ import annotations

from pathlib import Path

import yaml

from publicstack_contracts.validate.openapi import validate_openapi


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


def test_citations_exemplar_valid(examples_dir: Path):
    findings = validate_openapi(_load(examples_dir / "citations.v1.yaml"))
    assert findings == []


def test_permits_identity_exemplar_valid(examples_dir: Path):
    findings = validate_openapi(_load(examples_dir / "permits.identity.v1.yaml"))
    assert findings == []


def test_missing_openapi_field():
    findings = validate_openapi({"info": {"title": "x", "version": "1"}})
    assert any(f.path == "openapi" for f in findings)


def test_missing_publicstack_metadata():
    findings = validate_openapi({
        "openapi": "3.1.0",
        "info": {"title": "x", "version": "v1", "description": "y"},
        "paths": {},
    })
    paths = {f.path for f in findings}
    assert "info.x-publicstack-contract-name" in paths
    assert "info.x-publicstack-contract-version" in paths


def test_invalid_oas_structure():
    findings = validate_openapi({
        "openapi": "3.1.0",
        "info": {"title": "x", "version": "v1", "description": "y",
                 "x-publicstack-contract-name": "x",
                 "x-publicstack-contract-version": "v1"},
        "paths": "not a mapping",
    })
    assert any(f.path == "(structure)" for f in findings)
