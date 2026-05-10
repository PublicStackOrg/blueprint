from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from publicstack_contracts.diff.openapi import diff_openapi
from publicstack_contracts.diff.report import has_breaking


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


def test_identical_doc_no_breaking(examples_dir: Path):
    doc = _load(examples_dir / "citations.v1.yaml")
    findings = diff_openapi(deepcopy(doc), deepcopy(doc))
    assert not has_breaking(findings)


def test_removed_path_breaking(examples_dir: Path):
    old = _load(examples_dir / "citations.v1.yaml")
    new = deepcopy(old)
    new["paths"].pop("/citations/{id}")
    findings = diff_openapi(old, new)
    assert any(f.rule == "OAS-PATH-REMOVED" for f in findings)
    assert has_breaking(findings)


def test_removed_required_response_field_breaking(examples_dir: Path):
    old = _load(examples_dir / "citations.v1.yaml")
    new = deepcopy(old)
    citation = new["components"]["schemas"]["Citation"]
    citation["required"] = [r for r in citation["required"] if r != "amount_cents"]
    citation["properties"].pop("amount_cents")
    findings = diff_openapi(old, new)
    assert any(f.rule == "JS001" for f in findings)
    assert has_breaking(findings)


def test_removed_enum_value_breaking(examples_dir: Path):
    old = _load(examples_dir / "citations.v1.yaml")
    new = deepcopy(old)
    enum = new["components"]["schemas"]["CitationStatus"]["enum"]
    enum.remove("dismissed")
    findings = diff_openapi(old, new)
    assert any(f.rule == "JS004" for f in findings)
    assert has_breaking(findings)


def test_added_optional_field_not_breaking(examples_dir: Path):
    old = _load(examples_dir / "citations.v1.yaml")
    new = deepcopy(old)
    new["components"]["schemas"]["Citation"]["properties"]["paid_at"] = {
        "type": "string", "format": "date-time"
    }
    findings = diff_openapi(old, new)
    assert not has_breaking(findings)
