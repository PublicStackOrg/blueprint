# `docs/`

Long-form `blueprint` documentation. Different from the per-package
READMEs in sibling directories — these docs span the whole repo.

## What lives here

| File | What | Phase |
|---|---|---|
| `PLAN.md` | The phased plan for `blueprint` and the wider PublicStack ecosystem. The source of truth for what we're building and in what order. | seeded Phase 1, evolves continuously |
| `SPIKES.md` | Hard problems we know are coming but aren't ready to design yet (identity, payments execution, multi-tenancy, FOIA, audit immutability, hosting cost). Each entry has a forcing function — when it has to be resolved by. | seeded Phase 1 |
| `ARCHITECTURE.md` | Cross-cutting architecture notes for `blueprint` itself: how the template, CLI, compliance suite, contracts, and Grid fit together. | Phase 4 |
| `HOSTING.md` | Operator-facing hosting guide. Three on-ramps (single-VPS docker-compose / Helm / Terraform-per-cloud) with copy-pasteable runbooks. Optimized for cheap. | Phase 6 |
| `RFCs/` | RFCs proposing changes to `blueprint`. See [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for the process. | continuous |
| `migration-guides/` | Per-version-bump migration guides. `publicstack upgrade` walks each one. | continuous from Phase 3 |
