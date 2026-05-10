# SPDX-License-Identifier: AGPL-3.0-or-later
"""Audit adapter.

Append-only event log. Default impl is `PostgresAuditAdapter`, which writes
to the `audit_log` table created by Alembic migration 0002. Each row's
`entry_hash` is `sha256(prev_hash || canonical_json(row))`, giving a
verifiable chain. The first row's `prev_hash` is 32 zero bytes.

The Grid contract is at blueprint/grid/audit/contract.yaml. `prev_hash` and
`entry_hash` are optional in the contract so a future managed-audit adapter
(QLDB, immutable S3) can ship without a v2 of the audit contract.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    LargeBinary,
    MetaData,
    String,
    Table,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession

ActorKind = Literal["user", "service"]

_ZERO_HASH = b"\x00" * 32

_metadata = MetaData()

audit_log_table = Table(
    "audit_log",
    _metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("seq", BigInteger, nullable=False, unique=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("actor_id", String, nullable=False),
    Column("actor_kind", String, nullable=False),
    Column("action", String, nullable=False),
    Column("resource_kind", String, nullable=False),
    Column("resource_id", String, nullable=False),
    Column("payload", JSONB, nullable=False),
    Column("prev_hash", LargeBinary, nullable=False),
    Column("entry_hash", LargeBinary, nullable=False, unique=True),
    Index("ix_audit_log_occurred_at", "occurred_at"),
    Index("ix_audit_log_actor", "actor_id", "occurred_at"),
    Index("ix_audit_log_resource", "resource_kind", "resource_id", "occurred_at"),
)


@dataclass(frozen=True)
class Actor:
    id: str
    kind: ActorKind


@dataclass(frozen=True)
class Resource:
    kind: str
    id: str


@dataclass(frozen=True)
class AuditEntry:
    id: str
    seq: int
    occurred_at: datetime
    actor: Actor
    action: str
    resource: Resource
    payload: dict[str, Any] = field(default_factory=dict)
    prev_hash: bytes = _ZERO_HASH
    entry_hash: bytes = _ZERO_HASH


class AuditAdapter(Protocol):
    async def append(
        self,
        *,
        actor: Actor,
        action: str,
        resource: Resource,
        payload: dict[str, Any] | None = None,
    ) -> AuditEntry: ...

    async def query(
        self,
        *,
        resource: Resource | None = None,
        actor_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]: ...

    async def verify_chain(self, *, since: datetime | None = None) -> bool: ...


def _canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")


def _compute_entry_hash(prev_hash: bytes, row: dict[str, Any]) -> bytes:
    return hashlib.sha256(prev_hash + _canonical_json(row)).digest()


class PostgresAuditAdapter:
    """Append-only audit log against Postgres. Computes prev_hash/entry_hash."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        *,
        actor: Actor,
        action: str,
        resource: Resource,
        payload: dict[str, Any] | None = None,
    ) -> AuditEntry:
        # Serialize writers: lock the latest row so prev_hash is the actually-
        # last-committed entry.
        last = (
            await self._session.execute(
                text(
                    "SELECT entry_hash, seq FROM audit_log "
                    "ORDER BY seq DESC LIMIT 1 FOR UPDATE"
                )
            )
        ).first()
        prev_hash = bytes(last[0]) if last else _ZERO_HASH

        # Use the database's BIGSERIAL via insert without an explicit seq value.
        entry_id = uuid.uuid4()
        occurred_at = datetime.now(UTC)
        payload = payload or {}

        # Insert, returning the assigned seq so we can compute the hash with it.
        # Strategy: insert with a placeholder entry_hash, immediately read the
        # assigned seq back, then UPDATE with the correct hash. Both within the
        # outer transaction so external observers never see the placeholder.
        result = await self._session.execute(
            text(
                "INSERT INTO audit_log "
                "(id, occurred_at, actor_id, actor_kind, action, "
                "resource_kind, resource_id, payload, prev_hash, entry_hash) "
                "VALUES (:id, :occurred_at, :actor_id, :actor_kind, :action, "
                ":resource_kind, :resource_id, CAST(:payload AS jsonb), "
                ":prev_hash, :entry_hash) RETURNING seq"
            ),
            {
                "id": entry_id,
                "occurred_at": occurred_at,
                "actor_id": actor.id,
                "actor_kind": actor.kind,
                "action": action,
                "resource_kind": resource.kind,
                "resource_id": resource.id,
                "payload": json.dumps(payload, default=str),
                "prev_hash": prev_hash,
                "entry_hash": _ZERO_HASH,  # placeholder, updated below
            },
        )
        seq = result.scalar_one()

        canonical = {
            "actor_id": actor.id,
            "actor_kind": actor.kind,
            "action": action,
            "resource_kind": resource.kind,
            "resource_id": resource.id,
            "payload": payload,
            "occurred_at": occurred_at.isoformat(),
            "seq": seq,
        }
        entry_hash = _compute_entry_hash(prev_hash, canonical)

        await self._session.execute(
            text("UPDATE audit_log SET entry_hash = :h WHERE id = :id"),
            {"h": entry_hash, "id": entry_id},
        )

        return AuditEntry(
            id=str(entry_id),
            seq=seq,
            occurred_at=occurred_at,
            actor=actor,
            action=action,
            resource=resource,
            payload=payload,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )

    async def query(
        self,
        *,
        resource: Resource | None = None,
        actor_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        stmt = select(audit_log_table).order_by(audit_log_table.c.seq)
        if resource is not None:
            stmt = stmt.where(
                audit_log_table.c.resource_kind == resource.kind,
                audit_log_table.c.resource_id == resource.id,
            )
        if actor_id is not None:
            stmt = stmt.where(audit_log_table.c.actor_id == actor_id)
        if since is not None:
            stmt = stmt.where(audit_log_table.c.occurred_at >= since)
        stmt = stmt.limit(limit)
        rows = (await self._session.execute(stmt)).mappings().all()
        return [
            AuditEntry(
                id=str(r["id"]),
                seq=r["seq"],
                occurred_at=r["occurred_at"],
                actor=Actor(id=r["actor_id"], kind=r["actor_kind"]),
                action=r["action"],
                resource=Resource(kind=r["resource_kind"], id=r["resource_id"]),
                payload=dict(r["payload"] or {}),
                prev_hash=bytes(r["prev_hash"]),
                entry_hash=bytes(r["entry_hash"]),
            )
            for r in rows
        ]

    async def verify_chain(self, *, since: datetime | None = None) -> bool:
        stmt = select(audit_log_table).order_by(audit_log_table.c.seq)
        if since is not None:
            stmt = stmt.where(audit_log_table.c.occurred_at >= since)
        rows = (await self._session.execute(stmt)).mappings().all()

        expected_prev = _ZERO_HASH if since is None else None
        for r in rows:
            prev = bytes(r["prev_hash"])
            if expected_prev is not None and prev != expected_prev:
                return False
            canonical = {
                "actor_id": r["actor_id"],
                "actor_kind": r["actor_kind"],
                "action": r["action"],
                "resource_kind": r["resource_kind"],
                "resource_id": r["resource_id"],
                "payload": dict(r["payload"] or {}),
                "occurred_at": r["occurred_at"].isoformat(),
                "seq": r["seq"],
            }
            recomputed = _compute_entry_hash(prev, canonical)
            if recomputed != bytes(r["entry_hash"]):
                return False
            expected_prev = bytes(r["entry_hash"])
        return True
