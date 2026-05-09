# SPDX-License-Identifier: AGPL-3.0-or-later
"""Sanity tests for shared settings."""

from __future__ import annotations

import os
from unittest.mock import patch

from core.config import Settings


def _isolated_env(**overrides: str) -> dict[str, str]:
    """Build a clean env that only carries the keys we care about.

    Avoids picking up unrelated values from the host (e.g. CI sets
    SYNC_DATABASE_URL, which would silently shadow the derivation we're
    asserting on).
    """
    base = {k: v for k, v in os.environ.items() if not k.startswith(("DATABASE_URL", "SYNC_DATABASE_URL"))}
    base.update(overrides)
    return base


def test_async_dsn_to_sync_derivation():
    with patch.dict(
        os.environ,
        _isolated_env(DATABASE_URL="postgresql+asyncpg://u:p@h:5432/db"),
        clear=True,
    ):
        s = Settings()  # type: ignore[call-arg]
    assert s.derived_sync_database_url == "postgresql://u:p@h:5432/db"


def test_explicit_sync_dsn_wins():
    with patch.dict(
        os.environ,
        _isolated_env(
            DATABASE_URL="postgresql+asyncpg://u:p@h:5432/db",
            SYNC_DATABASE_URL="postgresql://other:other@elsewhere:5432/other",
        ),
        clear=True,
    ):
        s = Settings()  # type: ignore[call-arg]
    assert s.derived_sync_database_url == "postgresql://other:other@elsewhere:5432/other"
