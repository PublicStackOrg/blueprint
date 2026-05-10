"""Text + JSON formatters for compliance findings."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

from publicstack_compliance import __version__
from publicstack_compliance.findings import Finding

_RED = "\033[1;31m"
_YELLOW = "\033[1;33m"
_BLUE = "\033[1;34m"
_GREEN = "\033[1;32m"
_RESET = "\033[0m"


def _colorize() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _tag(severity: str) -> str:
    if not _colorize():
        return {"breaking": "[BREAK]", "warn": "[warn ]", "info": "[info ]"}[severity]
    color = {"breaking": _RED, "warn": _YELLOW, "info": _BLUE}[severity]
    text = {"breaking": "[BREAK]", "warn": "[warn ]", "info": "[info ]"}[severity]
    return f"{color}{text}{_RESET}"


def format_text(findings: list[Finding], ps_root: Path) -> str:
    lines: list[str] = []
    by_check: dict[str, list[Finding]] = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)

    for check_name in sorted(by_check):
        lines.append(f"\n  {check_name}:")
        for f in by_check[check_name]:
            loc = f" {f.location}" if f.location else ""
            lines.append(f"    {_tag(f.severity)} {f.rule}{loc}: {f.message}")
            if f.suggestion:
                lines.append(f"        {f.suggestion}")

    counts = Counter(f.severity for f in findings)
    summary_parts = [
        f"{counts.get('breaking', 0)} breaking",
        f"{counts.get('warn', 0)} warn",
        f"{counts.get('info', 0)} info",
    ]
    if findings:
        lines.append(f"\n  summary: {', '.join(summary_parts)}")
    else:
        green = f"{_GREEN}all checks passed{_RESET}" if _colorize() else "all checks passed"
        lines.append(f"\n  {green}")
    return "\n".join(lines).lstrip("\n")


def format_json(findings: list[Finding], ps_root: Path) -> str:
    payload = {
        "version": __version__,
        "ps_root": str(ps_root),
        "findings": [
            {
                "check": f.check,
                "rule": f.rule,
                "severity": f.severity,
                "location": f.location,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
        ],
        "summary": dict(Counter(f.severity for f in findings)),
    }
    return json.dumps(payload, indent=2, sort_keys=False)
