# SPDX-License-Identifier: AGPL-3.0-or-later
"""InMemoryAccessibilityAdapter sanity check."""

from __future__ import annotations

import pytest

from grid_adapters.accessibility import (
    A11yViolation,
    InMemoryAccessibilityAdapter,
)


@pytest.mark.asyncio
async def test_record_and_latest():
    adapter = InMemoryAccessibilityAdapter()
    violation = A11yViolation(
        rule_id="color-contrast",
        severity="serious",
        selector=".btn-primary",
        app="resident",
        app_route="/citations",
    )
    await adapter.record(violation)
    report = await adapter.latest("resident")
    assert report is not None
    assert report.app == "resident"
    assert violation in report.violations


@pytest.mark.asyncio
async def test_latest_for_unknown_app_is_none():
    adapter = InMemoryAccessibilityAdapter()
    assert await adapter.latest("nonexistent") is None
