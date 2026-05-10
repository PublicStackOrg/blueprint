from __future__ import annotations

import shutil
from pathlib import Path

from publicstack_compliance.checks.grid_integration import run
from publicstack_compliance.findings import has_breaking


def _by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


def test_minimal_ps_passes(ps_minimal: Path) -> None:
    findings = run(ps_minimal)
    assert not has_breaking(findings), findings


def test_missing_required_service_breaking(ps_minimal: Path) -> None:
    (ps_minimal / "grid/audit.yaml").unlink()
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "GRD-001" in by_rule
    assert any(
        f.severity == "breaking" and "audit" in f.message
        for f in by_rule["GRD-001"]
    )
    assert has_breaking(findings)


def test_missing_recommended_service_warn_not_breaking(ps_minimal: Path) -> None:
    (ps_minimal / "grid/notifications.yaml").unlink()
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    notif_findings = [
        f for f in by_rule.get("GRD-001", []) if "notifications" in f.message
    ]
    assert notif_findings
    assert all(f.severity == "warn" for f in notif_findings)


def test_invalid_backend_breaking(ps_minimal: Path) -> None:
    (ps_minimal / "grid/identity.yaml").write_text("backend: chickenwire\n")
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "GRD-002" in by_rule


def test_missing_adapter_breaking_for_required(ps_minimal: Path) -> None:
    shutil.rmtree(ps_minimal / "libraries/grid_adapters/grid_adapters/audit")
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "GRD-003" in by_rule
    audit = [f for f in by_rule["GRD-003"] if "audit" in f.message]
    assert audit and audit[0].severity == "breaking"


def test_missing_dependency_warn(ps_minimal: Path) -> None:
    deps = ps_minimal / "services/api/api/dependencies.py"
    deps.write_text("# no functions\n")
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "GRD-004" in by_rule
    assert all(f.severity == "warn" for f in by_rule["GRD-004"])


def test_payments_detected_without_yaml_emits_grd005(ps_minimal: Path) -> None:
    (ps_minimal / "grid/payments.yaml").unlink()
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "GRD-005" in by_rule
