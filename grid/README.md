# `grid/`

The blueprint-defined Grid contracts — the abstract shape of every
shared backbone service that Public Services consume.

**Status:** empty placeholder. Filled in during **Phase 4** of
[`../docs/PLAN.md`](../docs/PLAN.md).

The Grid is a **contract layer, not a deployed shared service.** Each
Public Service implements Grid contracts locally via adapters in its
own `libraries/grid_adapters/`. Public Services do not call out to a
centrally-deployed PublicStack-Grid instance — that keeps every Public
Service portable and self-hostable.

What lands here, one subdirectory per Grid service:

- `identity/` — auth contract. Default impl TBD per
  [`../docs/SPIKES.md`](../docs/SPIKES.md).
- `payments/` — payments contract. Model is city-direct: Public
  Services hand off to a city-provided processor; the contract defines
  the handoff shape. Execution details in `SPIKES.md`.
- `notifications/` — email/SMS/push contract.
- `audit/` — append-only audit log contract.
  Tamper-evidence/immutability story in `SPIKES.md`.
- `document_storage/` — object-storage contract.
- `accessibility/` — WCAG-checking helpers and a11y primitives shared
  across Flutter apps.

Each subdirectory ships: a contract spec, a default self-hostable
implementation, and adapter slots for managed providers.
