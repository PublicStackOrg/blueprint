# SPDX-License-Identifier: AGPL-3.0-or-later
"""LogOnlyAdapter for notifications."""

from __future__ import annotations

import logging

import pytest

from grid_adapters.notifications import LogOnlyAdapter


@pytest.mark.asyncio
async def test_log_only_emits_log(caplog):
    caplog.set_level(logging.INFO, logger="grid_adapters.notifications")
    adapter = LogOnlyAdapter()
    msg = await adapter.send(
        channel="email",
        to="someone@example.com",
        template_id="welcome",
        vars={"name": "Pat"},
    )
    assert msg.status == "delivered"
    assert any("notification (log-only)" in r.getMessage() for r in caplog.records)
    fetched = await adapter.get(msg.id)
    assert fetched is not None
    assert fetched.id == msg.id
