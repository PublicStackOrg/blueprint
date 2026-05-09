# SPDX-License-Identifier: AGPL-3.0-or-later
"""Sanity tests for shared settings."""

from __future__ import annotations

import os
from unittest.mock import patch

from core.config import Settings


def test_async_dsn_to_sync_derivation():
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql+asyncpg://u:p@h:5432/db"},
        clear=False,
    ):
        s = Settings()  # type: ignore[call-arg]
    assert s.derived_sync_database_url == "postgresql://u:p@h:5432/db"


def test_explicit_sync_dsn_wins():
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql+asyncpg://u:p@h:5432/db",
            "SYNC_DATABASE_URL": "postgresql://other:other@elsewhere:5432/other",
        },
        clear=False,
    ):
        s = Settings()  # type: ignore[call-arg]
    assert s.derived_sync_database_url == "postgresql://other:other@elsewhere:5432/other"
