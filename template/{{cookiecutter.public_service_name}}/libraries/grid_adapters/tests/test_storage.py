# SPDX-License-Identifier: AGPL-3.0-or-later
"""Adapter sanity tests."""

from __future__ import annotations

from grid_adapters.identity import NoAuthAdapter
from grid_adapters.notifications import LogOnlyAdapter
from grid_adapters.storage import LocalFilesystemAdapter


def test_local_filesystem_roundtrip(tmp_path):
    adapter = LocalFilesystemAdapter(tmp_path)
    url = adapter.put("hello.txt", b"hi")
    assert url.startswith("file://")
    assert adapter.get("hello.txt") == b"hi"


async def test_no_auth_returns_dev_user():
    adapter = NoAuthAdapter()
    user = await adapter.current_user(token=None)
    assert user is not None
    assert user.id == "dev-user"
    assert user.is_staff is True


def test_log_only_notifications(caplog):
    adapter = LogOnlyAdapter()
    adapter.send(to="someone@example.com", subject="hi", body="test")
    assert any("notification (log-only)" in r.message for r in caplog.records)
