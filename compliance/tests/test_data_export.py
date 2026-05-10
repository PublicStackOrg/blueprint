from __future__ import annotations

from pathlib import Path

from publicstack_compliance.checks.data_export import run
from publicstack_compliance.findings import has_breaking


def _findings_by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


def test_minimal_ps_passes_with_complete_model_and_routes(ps_minimal: Path) -> None:
    findings = run(ps_minimal)
    assert not has_breaking(findings), findings


def test_missing_export_route_fires_dex001(ps_minimal: Path) -> None:
    # Remove the export router; both Item and Citation should fire DEX-001.
    (ps_minimal / "services/api/api/routers/v1/export_router.py").unlink()

    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "DEX-001" in by_rule
    assert len(by_rule["DEX-001"]) == 2  # Item + Citation
    messages = " ".join(f.message for f in by_rule["DEX-001"])
    assert "Item" in messages
    assert "Citation" in messages
    assert has_breaking(findings)


def test_missing_export_test_fires_dex002(ps_minimal: Path) -> None:
    (ps_minimal / "services/api/tests/test_export.py").unlink()
    findings = run(ps_minimal)
    by_rule = _findings_by_rule(findings)
    assert "DEX-002" in by_rule
    assert len(by_rule["DEX-002"]) == 2
    # warn, not breaking
    assert not has_breaking(findings)


def test_no_models_fires_dex004(tmp_path: Path) -> None:
    # PS root with BLUEPRINT_VERSION but no libraries/core/.
    (tmp_path / "BLUEPRINT_VERSION").write_text("0.3.0\n")
    findings = run(tmp_path)
    by_rule = _findings_by_rule(findings)
    assert "DEX-004" in by_rule
    assert "no model files" in by_rule["DEX-004"][0].message


def test_models_with_no_base_subclasses_fires_dex004(tmp_path: Path) -> None:
    (tmp_path / "BLUEPRINT_VERSION").write_text("0.3.0\n")
    models = tmp_path / "libraries/core/core/db/models.py"
    models.parent.mkdir(parents=True)
    models.write_text("def helper():\n    pass\n")
    findings = run(tmp_path)
    by_rule = _findings_by_rule(findings)
    assert "DEX-004" in by_rule
    assert "no model classes" in by_rule["DEX-004"][0].message


def test_malformed_model_file_fires_dex004(tmp_path: Path) -> None:
    (tmp_path / "BLUEPRINT_VERSION").write_text("0.3.0\n")
    models = tmp_path / "libraries/core/core/db/models.py"
    models.parent.mkdir(parents=True)
    # Genuine SyntaxError: unbalanced paren.
    models.write_text("class Item(Base):\n    pass\ndef broken(:\n")
    findings = run(tmp_path)
    by_rule = _findings_by_rule(findings)
    assert "DEX-004" in by_rule
