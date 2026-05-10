"""Check registry. Each check module exposes NAME + run(ps_root)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from publicstack_compliance.checks import (
    accessibility,
    contract_compat,
    data_export,
    grid_integration,
    observability,
    security,
)
from publicstack_compliance.findings import Finding

CHECKS: dict[str, Callable[[Path], list[Finding]]] = {
    "data_export": data_export.run,
    "contract_compat": contract_compat.run,
    "grid_integration": grid_integration.run,
    "security": security.run,
    "observability": observability.run,
    "accessibility": accessibility.run,
}


def list_check_names() -> list[str]:
    return sorted(CHECKS.keys())
