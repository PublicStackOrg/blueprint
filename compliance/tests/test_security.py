from __future__ import annotations

from pathlib import Path

import pytest

from publicstack_compliance.checks import security
from publicstack_compliance.findings import has_breaking


def _by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


@pytest.fixture(autouse=True)
def _stub_pip_audit_and_gitleaks(monkeypatch):
    """Avoid hitting real subprocesses during unit tests."""
    monkeypatch.setattr(security, "_run_pip_audit", lambda _d: ([], False))
    monkeypatch.setattr(security, "_run_gitleaks", lambda _r: ([], False))
    # Always pretend gitleaks isn't on PATH so we hit the SEC-006 warn path.
    monkeypatch.setattr(security.shutil, "which", lambda _name: None)


def test_minimal_ps_passes_csp_and_https(ps_minimal: Path) -> None:
    findings = security.run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "SEC-003" not in by_rule
    assert "SEC-004" not in by_rule
    assert not has_breaking(findings)


def test_missing_csp_emits_sec003(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace("Content-Security-Policy", "X-Other")
    main.write_text(text)
    findings = security.run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "SEC-003" in by_rule
    assert has_breaking(findings)


def test_missing_https_redirect_emits_sec004(ps_minimal: Path) -> None:
    main = ps_minimal / "services/api/api/main.py"
    text = main.read_text().replace("HTTPSRedirectMiddleware", "NoOpMiddleware")
    main.write_text(text)
    findings = security.run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "SEC-004" in by_rule


def test_hardcoded_secret_emits_sec005(ps_minimal: Path) -> None:
    deps = ps_minimal / "services/api/api/dependencies.py"
    deps.write_text(deps.read_text() + "\n\nDEFAULT_TOKEN = \"abc-not-good\"\n")
    findings = security.run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "SEC-005" in by_rule
    assert has_breaking(findings)


def test_missing_tools_emits_sec006_warn(ps_minimal: Path) -> None:
    findings = security.run(ps_minimal)
    by_rule = _by_rule(findings)
    assert "SEC-006" in by_rule
    # Warn, not breaking — pipx-only installs without pip-audit/gitleaks
    # should still see the rest of the suite work.
    assert all(f.severity == "warn" for f in by_rule["SEC-006"])
