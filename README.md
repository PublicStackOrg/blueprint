# blueprint

The template + spec every PublicStack Public Service is generated from.

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](./LICENSE)

## What this is

`blueprint` defines the shape of a Public Service — its directory
layout, its dependencies, the contracts it must implement to talk to
other Public Services and to shared infrastructure, and the compliance
checks that prove it does. Every Public Service in the PublicStack
ecosystem (Parking, Permits, 311, …) starts as a generation from
`blueprint`, then evolves on its own.

`blueprint` is **not a runtime framework.** Public Services don't
import a `publicstack` package and call into it at request time. They
copy the shape, declare which `blueprint` version they were generated
from in their `BLUEPRINT_VERSION` file, and use the `publicstack` CLI
(see Phase 3 of [`docs/PLAN.md`](./docs/PLAN.md)) to upgrade when new
versions ship.

## Vocabulary

| Term | Meaning |
|---|---|
| **PublicStack** | The ecosystem / org / standard. |
| **Public Service** | One deployable civic application — its own monorepo, its own AGPL repo. e.g. Parking, Permits, 311. |
| **internal service** / **backend service** | A microservice inside one Public Service. e.g. `api`, `worker`, `migrator`. |
| **app** / **frontend** | A Flutter app inside one Public Service. e.g. `apps/resident`, `apps/staff`. |
| **library** | A shared Python or Dart package inside one Public Service. |
| **Contract** | A versioned schema one Public Service exposes to others. (Parking exposes `citations.v1`; Permits consumes it.) |
| **Grid** | Shared backbone services (identity, payments, notifications, audit, document storage, accessibility) consumed by every Public Service via adapters. The Grid is a contract layer, not a deployed shared service. |
| **Compliance suite** | The test pack that verifies a Public Service meets PublicStack standards. |
| **`blueprint`** | This repo. The template + spec. |

## How to use it

Once the `publicstack` CLI ships (Phase 3 of `docs/PLAN.md`):

```bash
publicstack new service parking
```

…produces a working `parking/` Public Service tree. Until the CLI
lands, the template is generated directly via `cookiecutter` against
the `template/` subdir — see `docs/PLAN.md` for the manual recipe.

## What's inside

```
blueprint/
├── template/      cookiecutter scaffold for a new Public Service     (Phase 2)
├── compliance/    Python package: PublicStack compliance checks      (Phase 5)
├── cli/           Python package: the `publicstack` CLI              (Phase 3)
├── contracts/     core Contracts + the Contract format spec          (Phase 4)
├── grid/          Grid service contract definitions                  (Phase 4)
└── docs/          PLAN, SPIKES, ARCHITECTURE, HOSTING, RFCs
```

Each subdirectory has its own README explaining what lives there and
which phase of `docs/PLAN.md` populates it.

## Status

`blueprint` is currently at **Phase 1 of 8**: repo skeleton. No
generation works yet. Track progress in
[`docs/PLAN.md`](./docs/PLAN.md); known hard problems are in
[`docs/SPIKES.md`](./docs/SPIKES.md).

## Why open source

PublicStack's thesis: civic software should be open, the data
exportable, and the operator switchable. AGPL-3.0 is the strongest
practical guarantee that those properties survive contact with
commercial hosting. See [`LICENSING.md`](./LICENSING.md) for the
rationale; the broader ecosystem pitch is at
<https://publicstack.org>.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Substantive changes go
through the RFC process; small fixes can land directly. Project spaces
follow the [Contributor Covenant 2.1](./CODE_OF_CONDUCT.md).

For security disclosure, see [`SECURITY.md`](./SECURITY.md).

## License

[AGPL-3.0](./LICENSE) — the org-wide default for every PublicStack
repo. See [`LICENSING.md`](./LICENSING.md) for why.
