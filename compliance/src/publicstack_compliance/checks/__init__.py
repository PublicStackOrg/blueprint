"""Check registry. Each check module exposes NAME + run(ps_root)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from publicstack_compliance.checks import contract_compat, data_export, grid_integration
from publicstack_compliance.findings import Finding


def _stub(name: str) -> Callable[[Path], list[Finding]]:
    def _run(_ps_root: Path) -> list[Finding]:
        return [
            Finding(
                check=name,
                rule=f"{name.upper().split('_')[0][:3]}-000",
                severity="info",
                location="",
                message=f"check '{name}' is a Phase 5 stub; implementation pending",
            )
        ]

    return _run


CHECKS: dict[str, Callable[[Path], list[Finding]]] = {
    "data_export": data_export.run,
    "contract_compat": contract_compat.run,
    "grid_integration": grid_integration.run,
    "security": _stub("security"),
    "observability": _stub("observability"),
    "accessibility": _stub("accessibility"),
}


def list_check_names() -> list[str]:
    return sorted(CHECKS.keys())
