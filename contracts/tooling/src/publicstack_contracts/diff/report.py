"""Common Finding/Severity types for back-compat diffs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["breaking", "info"]


@dataclass(frozen=True)
class Finding:
    rule: str           # e.g. "JS001"
    severity: Severity
    path: str           # JSON-pointer-style path to the offending location
    message: str

    def is_breaking(self) -> bool:
        return self.severity == "breaking"


def has_breaking(findings: list[Finding]) -> bool:
    return any(f.is_breaking() for f in findings)
