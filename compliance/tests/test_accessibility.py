from __future__ import annotations

from pathlib import Path

from publicstack_compliance.checks import accessibility
from publicstack_compliance.findings import has_breaking


def _by_rule(findings):
    out: dict[str, list] = {}
    for f in findings:
        out.setdefault(f.rule, []).append(f)
    return out


def test_no_apps_dir_returns_empty(tmp_path: Path) -> None:
    findings = accessibility.run(tmp_path)
    assert findings == []


def test_no_web_build_emits_a11y005(tmp_path: Path) -> None:
    apps = tmp_path / "apps" / "resident"
    apps.mkdir(parents=True)
    findings = accessibility.run(tmp_path)
    by_rule = _by_rule(findings)
    assert "A11Y-005" in by_rule
    assert not has_breaking(findings)


def test_playwright_missing_emits_a11y006(
    tmp_path: Path, monkeypatch
) -> None:
    apps = tmp_path / "apps" / "resident" / "build" / "web"
    apps.mkdir(parents=True)
    (apps / "index.html").write_text("<html></html>")
    monkeypatch.setattr(accessibility, "_playwright_available", lambda: False)
    findings = accessibility.run(tmp_path)
    by_rule = _by_rule(findings)
    assert "A11Y-006" in by_rule
    assert all(f.severity == "warn" for f in by_rule["A11Y-006"])


def test_axe_violations_map_to_rules(tmp_path: Path, monkeypatch) -> None:
    apps = tmp_path / "apps" / "resident" / "build" / "web"
    apps.mkdir(parents=True)
    (apps / "index.html").write_text("<html></html>")
    monkeypatch.setattr(accessibility, "_playwright_available", lambda: True)

    # Stub the Playwright run by replacing _scan_app itself.
    fake_findings_payload = [
        {
            "id": "color-contrast",
            "impact": "serious",
            "help": "Elements must have sufficient contrast",
            "helpUrl": "https://example.org/contrast",
            "nodes": [{"target": [".btn-primary"]}],
        },
        {
            "id": "image-alt",
            "impact": "minor",
            "help": "Images need alt text",
            "nodes": [{"target": ["img"]}],
        },
    ]

    def fake_scan(app_dir: Path):
        from publicstack_compliance.findings import Finding
        out = []
        for v in fake_findings_payload:
            impact = v["impact"]
            rule_id, severity = accessibility._SEVERITY_MAP[impact]
            target = v["nodes"][0]["target"][0]
            out.append(Finding(
                check=accessibility.NAME,
                rule=rule_id,
                severity=severity,
                location=f"apps/{app_dir.name} {target}",
                message=f"{v['id']}: {v['help']}",
                suggestion=v.get("helpUrl"),
            ))
        return out

    monkeypatch.setattr(accessibility, "_scan_app", fake_scan)
    findings = accessibility.run(tmp_path)
    by_rule = _by_rule(findings)
    assert "A11Y-002" in by_rule  # serious
    assert "A11Y-004" in by_rule  # minor
    assert has_breaking(findings)


def test_severity_map_completeness() -> None:
    assert set(accessibility._SEVERITY_MAP.keys()) == {
        "critical", "serious", "moderate", "minor"
    }
