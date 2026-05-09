# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared pytest fixtures.

Test files in services/api, services/worker, etc. import these fixtures
to set up a real Postgres database, async sessions, an httpx client
against the FastAPI app, and factory helpers.
"""

from test_helper.fixtures import (  # noqa: F401
    async_session,
    db_engine,
    test_database_url,
)
