# SPDX-License-Identifier: AGPL-3.0-or-later
"""Accessibility adapter.

Records WCAG 2.2 AA violations from automated scans of generated Flutter
apps. The Grid contract is at blueprint/grid/accessibility/contract.yaml.

The default in-memory adapter is what tests use; cities can swap in a
persisted adapter once they want historical scan reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol

Severity = Literal["minor", "moderate", "serious", "critical"]


@dataclass(frozen=True)
class A11yViolation:
    rule_id: str
    severity: Severity
    selector: str
    app: str
    app_route: str
    help_url: str | None = None


@dataclass(frozen=True)
class A11yScanReport:
    generated_at: datetime
    app: str
    violations: tuple[A11yViolation, ...]


class AccessibilityAdapter(Protocol):
    async def record(self, violation: A11yViolation) -> None: ...
    async def latest(self, app: str) -> A11yScanReport | None: ...


class InMemoryAccessibilityAdapter:
    """Single-process violation buffer. Resets on restart."""

    def __init__(self) -> None:
        self._by_app: dict[str, list[A11yViolation]] = {}

    async def record(self, violation: A11yViolation) -> None:
        self._by_app.setdefault(violation.app, []).append(violation)

    async def latest(self, app: str) -> A11yScanReport | None:
        violations = self._by_app.get(app)
        if not violations:
            return None
        return A11yScanReport(
            generated_at=datetime.now(UTC),
            app=app,
            violations=tuple(violations),
        )
