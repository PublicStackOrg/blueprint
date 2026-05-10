"""Orchestrator: runs the selected checks and returns aggregated findings."""

from __future__ import annotations

from pathlib import Path

from publicstack_compliance.checks import CHECKS
from publicstack_compliance.findings import Finding


def run_checks(ps_root: Path, names: list[str] | None = None) -> list[Finding]:
    """Run `names` (or all registered checks if None) against `ps_root`."""
    selected = names or list(CHECKS.keys())
    findings: list[Finding] = []
    for name in selected:
        if name not in CHECKS:
            raise KeyError(f"unknown check: {name!r}")
        findings.extend(CHECKS[name](ps_root))
    return findings
