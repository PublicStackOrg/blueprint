from __future__ import annotations

import json
from pathlib import Path

from publicstack_compliance.findings import Finding
from publicstack_compliance.report import format_json, format_text


def _sample() -> list[Finding]:
    return [
        Finding(check="data_export", rule="DEX-001", severity="breaking",
                location="services/api/api/routers/v1_router.py",
                message="Item has no /export/items route",
                suggestion="add a route under v1/export_router.py"),
        Finding(check="security", rule="SEC-006", severity="warn",
                location="", message="gitleaks not on PATH"),
    ]


def test_text_includes_rule_and_message():
    out = format_text(_sample(), Path("/tmp/ps"))
    assert "DEX-001" in out
    assert "Item has no /export/items route" in out
    assert "SEC-006" in out
    assert "summary" in out


def test_text_passes_when_empty():
    out = format_text([], Path("/tmp/ps"))
    assert "all checks passed" in out


def test_json_payload_shape():
    out = format_json(_sample(), Path("/tmp/ps"))
    parsed = json.loads(out)
    assert parsed["ps_root"] == "/tmp/ps"
    assert len(parsed["findings"]) == 2
    assert parsed["summary"]["breaking"] == 1
    assert parsed["summary"]["warn"] == 1
