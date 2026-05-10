# SPDX-License-Identifier: AGPL-3.0-or-later
"""LogOnlyPaymentsAdapter sanity check."""

from __future__ import annotations

import pytest

from grid_adapters.payments import LogOnlyPaymentsAdapter


@pytest.mark.asyncio
async def test_create_and_get_intent():
    adapter = LogOnlyPaymentsAdapter()
    intent = await adapter.create_intent(
        amount_cents=1000,
        currency="USD",
        description="Citation #1",
        return_url="https://example.org/done",
    )
    assert intent.amount_cents == 1000
    assert intent.currency == "USD"
    assert intent.status == "succeeded"
    assert intent.redirect_url == "https://example.org/done"

    fetched = await adapter.get_intent(intent.id)
    assert fetched is not None
    assert fetched.id == intent.id
