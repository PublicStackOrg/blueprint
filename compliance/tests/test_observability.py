from __future__ import annotations

from pathlib import Path

from publicstack_compliance.checks.observability import run
from publicstack_compliance.findings import has_breaking


def _by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


def test_minimal_ps_passes(ps_minimal: Path) -> None:
    findings = run(ps_minimal)
    assert not has_breaking(findings), findings


def test_missing_metrics_emits_obs001(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace("Instrumentator", "NoOpInstrumentor")
    main.write_text(text)
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "OBS-001" in by_rule
    assert has_breaking(findings)


def test_missing_otel_emits_obs002(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace("FastAPIInstrumentor", "FakeInstrumentor")
    main.write_text(text)
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "OBS-002" in by_rule


def test_missing_json_logger_emits_obs003(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace("pythonjsonlogger", "regular_logger")
    main.write_text(text)
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "OBS-003" in by_rule


def test_missing_log_fields_emits_obs004(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace('"trace_id"', '"trace_xxxx"')
    main.write_text(text)
    findings = run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "OBS-004" in by_rule
    assert all(f.severity == "warn" for f in by_rule["OBS-004"])


def test_missing_main_emits_obs001(tmp_path: Path) -> None:
    (tmp_path / "BLUEPRINT_VERSION").write_text("0.3.0\n")
    findings = run(tmp_path)
    by_rule = _by_rule(findings)
    assert "OBS-001" in by_rule
    assert any("not found" in f.message for f in by_rule["OBS-001"])
