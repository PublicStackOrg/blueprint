from __future__ import annotations

from publicstack_compliance.findings import (
    Finding,
    has_breaking,
    upgrade_warns_to_breaking,
)


def test_finding_is_breaking_predicate():
    f = Finding(check="x", rule="X-1", severity="breaking", location="", message="m")
    assert f.is_breaking()
    g = Finding(check="x", rule="X-2", severity="warn", location="", message="m")
    assert not g.is_breaking()


def test_has_breaking_with_mixed():
    findings = [
        Finding(check="x", rule="X-1", severity="warn", location="", message="m"),
        Finding(check="x", rule="X-2", severity="breaking", location="", message="m"),
    ]
    assert has_breaking(findings)


def test_has_breaking_with_only_warns():
    findings = [
        Finding(check="x", rule="X-1", severity="warn", location="", message="m"),
        Finding(check="x", rule="X-2", severity="info", location="", message="m"),
    ]
    assert not has_breaking(findings)


def test_strict_upgrade_warns_to_breaking():
    findings = [
        Finding(check="x", rule="X-1", severity="warn", location="", message="m"),
        Finding(check="x", rule="X-2", severity="info", location="", message="m"),
    ]
    upgraded = upgrade_warns_to_breaking(findings)
    assert upgraded[0].severity == "breaking"
    assert upgraded[1].severity == "info"
