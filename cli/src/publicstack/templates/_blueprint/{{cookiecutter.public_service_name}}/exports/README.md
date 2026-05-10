# `exports/`

Required data export endpoints — every entity in
`libraries/core/db/models.py` must have a working export route here.
Easy to leave is a PublicStack non-negotiable.

Filled in during **Phase 5** of `blueprint`'s plan, when the compliance
suite enforces this rule. For now, the API ships placeholder export
routes alongside the example `Item` CRUD.

Public-records / FOIA-specific concerns are tracked in
`blueprint/docs/SPIKES.md`; expect this directory's shape to evolve as
that spike resolves.
