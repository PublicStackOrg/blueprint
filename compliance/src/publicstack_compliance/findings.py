"""Finding dataclass + Severity Literal + Check Protocol."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal, Protocol

Severity = Literal["breaking", "warn", "info"]


@dataclass(frozen=True)
class Finding:
    check: str            # "data_export"
    rule: str             # "DEX-001"
    severity: Severity
    location: str         # path or "" for repo-level
    message: str
    suggestion: str | None = None

    def is_breaking(self) -> bool:
        return self.severity == "breaking"


class Check(Protocol):
    NAME: ClassVar[str]

    def run(self, ps_root: Path) -> list[Finding]: ...


def has_breaking(findings: list[Finding]) -> bool:
    return any(f.is_breaking() for f in findings)


def upgrade_warns_to_breaking(findings: list[Finding]) -> list[Finding]:
    """Used by --strict mode."""
    return [
        Finding(
            check=f.check,
            rule=f.rule,
            severity="breaking" if f.severity == "warn" else f.severity,
            location=f.location,
            message=f.message,
            suggestion=f.suggestion,
        )
        for f in findings
    ]
