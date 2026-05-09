# SPDX-License-Identifier: AGPL-3.0-or-later
"""Reusable pytest fixtures for {{ cookiecutter.public_service_name }} tests.

The compliance suite (Phase 5) requires tests to hit a real Postgres,
not a mock. These fixtures provide the wiring.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.db.base import Base
from core.db.models import Item  # noqa: F401  -- imported for metadata side effects


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Override via TEST_DATABASE_URL in CI."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test",
    )


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_database_url: str):
    engine = create_async_engine(test_database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(db_engine) -> AsyncIterator[AsyncSession]:
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
