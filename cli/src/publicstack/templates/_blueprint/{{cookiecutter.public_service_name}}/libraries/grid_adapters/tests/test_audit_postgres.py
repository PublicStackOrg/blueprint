# SPDX-License-Identifier: AGPL-3.0-or-later
"""PostgresAuditAdapter against a real Postgres.

The compose `db` service is the test database. CI brings it up before
running this suite. Locally: `docker compose up -d db migrator` first.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator

import pytest
from grid_adapters.audit import (
    Actor,
    PostgresAuditAdapter,
    Resource,
    audit_log_table,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://{{ cookiecutter.python_package }}:"
    "{{ cookiecutter.python_package }}@localhost:5432/"
    "{{ cookiecutter.python_package }}",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:  # noqa: D401
    return "asyncio"


@pytest.fixture()
async def session() -> AsyncIterator[AsyncSession]:
    """Yield a session against a freshly-isolated `audit_log` table state.

    The fixture truncates `audit_log` (which Alembic migration 0002 created)
    so tests run independently. If the table is missing, the test errors —
    that means the migrator service hasn't run.
    """
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=None)
    Maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with Maker() as s:
            await s.execute(text("TRUNCATE TABLE audit_log RESTART IDENTITY"))
            await s.commit()
        async with Maker() as s:
            yield s
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_append_and_query_round_trip(session: AsyncSession) -> None:
    adapter = PostgresAuditAdapter(session)
    actor = Actor(id="alice", kind="user")
    resource = Resource(kind="citation", id=str(uuid.uuid4()))

    e1 = await adapter.append(actor=actor, action="citation.created", resource=resource)
    e2 = await adapter.append(
        actor=actor, action="citation.updated", resource=resource, payload={"status": "paid"}
    )
    await session.commit()

    assert e1.seq < e2.seq
    assert e2.prev_hash == e1.entry_hash
    assert bytes(e1.prev_hash) == b"\x00" * 32

    rows = await adapter.query(resource=resource)
    assert [r.id for r in rows] == [e1.id, e2.id]


@pytest.mark.asyncio
async def test_verify_chain_passes(session: AsyncSession) -> None:
    adapter = PostgresAuditAdapter(session)
    for i in range(5):
        await adapter.append(
            actor=Actor(id="bob", kind="user"),
            action="resource.touched",
            resource=Resource(kind="thing", id=str(i)),
        )
    await session.commit()
    assert await adapter.verify_chain() is True


@pytest.mark.asyncio
async def test_verify_chain_detects_tampering(session: AsyncSession) -> None:
    adapter = PostgresAuditAdapter(session)
    for i in range(3):
        await adapter.append(
            actor=Actor(id="carol", kind="user"),
            action="resource.touched",
            resource=Resource(kind="thing", id=str(i)),
        )
    await session.commit()

    # Tamper with row 2's payload via raw SQL.
    await session.execute(
        text(
            "UPDATE audit_log SET payload = '{\"tampered\": true}'::jsonb "
            "WHERE seq = 2"
        )
    )
    await session.commit()

    assert await adapter.verify_chain() is False
