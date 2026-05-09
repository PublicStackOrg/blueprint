# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pytest fixtures for the API service.

Tests run against a real Postgres (CI service container or a local
docker-compose `db`). The `async_client` fixture wires the FastAPI app
against the test database via session-maker override.
"""

from __future__ import annotations

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.db.base import Base
from core.db.models import Item  # noqa: F401  -- registers metadata


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test",
    )
    engine = create_async_engine(url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(test_engine):
    from src.main import app

    app.state.db_engine = test_engine
    app.state.db_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
