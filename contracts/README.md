# `contracts/`

The blueprint-defined core Contracts and the Contract format spec.
Public Services use Contracts to talk to each other — Parking exposes
`citations.v1`, Permits consumes it, etc.

**Status:** empty placeholder. Filled in during **Phase 4** of
[`../docs/PLAN.md`](../docs/PLAN.md).

What lands here:

- `README.md` (in addition to this stub) — the **Contract format
  spec**: what a contract definition file must contain, how versioning
  works, how back-compat is enforced.
- `examples/` — exemplar contracts (audit log, identity, etc.) that
  reference Public Services can crib from.
- `tooling/` — schema validators and codegen for client/server stubs.

Per-Public-Service Contracts (the ones a specific Public Service
exposes or consumes) live in that Public Service's own
`contracts/exposed/` and `contracts/consumed/` directories — not here.
