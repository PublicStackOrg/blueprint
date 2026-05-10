# SPDX-License-Identifier: AGPL-3.0-or-later
"""NoAuthAdapter sanity check."""

from __future__ import annotations

import pytest

from grid_adapters.identity import NoAuthAdapter


@pytest.mark.asyncio
async def test_no_auth_returns_dev_user():
    adapter = NoAuthAdapter()
    user = await adapter.current_user(token=None)
    assert user is not None
    assert user.id == "dev-user"
    assert user.is_staff is True
