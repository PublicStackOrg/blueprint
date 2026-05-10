# Grid audit

Append-only log of state-mutating actions, with optional tamper-evidence.

## Contract

[`contract.yaml`](./contract.yaml) — JSON Schema 2020-12 for an audit log
entry. `prev_hash` and `entry_hash` are optional so adapters that delegate
tamper-evidence to a managed service (QLDB, immutable S3) can ship without a
v2.

## Default adapter

`libraries/grid_adapters/grid_adapters/audit/PostgresAuditAdapter` writes to
an `audit_log` table created by Alembic migration `0002_audit_log`. Computes
`entry_hash = SHA256(prev_hash || canonical_json(entry))`. Serializes writers
via `SELECT … FOR UPDATE` on the latest row to guarantee `prev_hash`
ordering.

### Throughput

Single-writer serialization. Adequate for civic workloads (a small-city
Parking deploy writes well under 10/s). See SPIKES.md #6 for the QLDB or
externally-anchored adapter path if higher throughput is needed.

### Verifying the chain

`PostgresAuditAdapter.verify_chain()` walks rows in `seq` order and recomputes
hashes; raises on mismatch. The compliance suite calls this in Phase 5.

The first row's `prev_hash` is 32 zero bytes (base64-encoded
`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=`). External auditors verifying
the chain start there.

## Env vars

- `AUDIT_BACKEND` — `postgres` (default), future: `qldb`, `s3_object_lock`, ...

## Out of scope for v1

- Hash-chain verification on the hot read path (currently a periodic job).
- External Merkle-root publication (SPIKES.md #6).
