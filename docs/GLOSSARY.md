# PublicStack glossary

A reference for the terms PublicStack uses. Read this before
[`PLAN.md`](./PLAN.md) — those docs assume this vocabulary.

## The big four

### PublicStack

The **ecosystem**: the org (`github.com/PublicStackOrg`), the standard
(blueprint), and the set of civic apps built on it. Not a runtime,
not a deployable thing — the umbrella name for everything else here.

### Public Service

A **deployable civic application**. Each Public Service is its own
GitHub repo, its own AGPL-3.0-licensed monorepo, operationally
independent of every other Public Service. Examples (real and
planned): **Parking**, **Permits**, **311**, **Licensing**, **Court
Scheduler**.

A Public Service is what a city actually deploys. One Public Service
holds everything that makes that civic concern work: backend services,
Flutter apps, the database, the deployment manifests, the docs.

Public Services do **not** call out to a centrally-deployed
PublicStack server. There is no such server. They talk to each other
through Contracts, and they implement shared infrastructure locally
through Grid adapters. That portability is deliberate — a city can
take a Public Service repo, fork it, and run it without depending on
us.

> Used to be called "Block" in earlier drafts. That word is gone.
> Always say "Public Service".

### internal service / backend service

A **microservice inside one Public Service**. Lives under `services/`
in the repo. Examples in a generated PS: `services/api` (FastAPI),
`services/worker` (RQ), `services/migrator` (Alembic).

The word matters: a *Public Service* is the whole repo (Parking),
while *services* under it are the moving parts (api, worker). When
the docs say "service" without qualification, watch the context — but
the unqualified word usually means an internal service.

### app / frontend

A **Flutter app** under `apps/` in the Public Service repo. Each
Public Service typically ships several:

- `apps/resident/` — what the public uses
- `apps/staff/` — what city employees use
- `apps/kiosk/` — terminal/in-person interface

All apps share a common design system in `libraries/ui/`.

## Smaller pieces inside a Public Service

### library

A **shared package inside one Public Service**, lives under
`libraries/`. Python or Dart. Examples: `libraries/core` (SQLAlchemy
models, config), `libraries/ui` (Flutter design system),
`libraries/grid_adapters` (the Grid adapter implementations — see
below).

A library is workspace-internal — never published to PyPI or
pub.dev. Other Public Services can't depend on a library; that's
what Contracts are for.

### Contract

A **versioned schema one Public Service exposes to other Public
Services, or consumes from them**. A contract is a YAML file
(OpenAPI 3.1 for HTTP-shaped contracts, JSON Schema for non-HTTP
shapes), versioned by major number (`v1`, `v2`, ...).

Two directories per Public Service:

- `contracts/exposed/` — contracts this Public Service publishes.
  Owned here.
- `contracts/consumed/` — pinned copies of other Public Services'
  exposed contracts. When the producer ships a v2, the consumer
  updates its pinned copy.

Example: Parking exposes `citations.v1.yaml`. Permits, when it wants
to check for outstanding citations before issuing a contractor
permit, has a copy of that file in its `contracts/consumed/` and
calls Parking's API.

The format spec lives at `blueprint/contracts/README.md`. The
`publicstack-contracts` CLI validates contracts and detects
breaking changes between versions.

## The Grid

This is the piece that confuses people most. Read carefully.

### What the Grid is

The Grid is a **set of contracts for shared backbone capabilities**:
identity, payments, notifications, audit, document_storage,
accessibility. Six services. Each is an interface every Public
Service implements locally.

### What the Grid is *not*

- **Not a deployed shared service.** There is no `grid.publicstack.org`.
- **Not a runtime PublicStack imports.** A Public Service doesn't `pip
  install publicstack-grid`.
- **Not a service mesh.** Nothing routes through a central instance.

### How the Grid actually works

Every generated Public Service has:

- `grid/<service>.yaml` — config picking the backend for that Grid
  service (e.g., `audit.yaml: backend: postgres`).
- `libraries/grid_adapters/grid_adapters/<service>/` — the **adapter
  code** that implements that Grid service inside this Public Service.

The Grid is a **contract layer** — it defines what `audit`,
`identity`, `payments`, etc. *mean* across PublicStack, but the
implementations live inside each Public Service. Swap the adapter
(via the YAML config + an env var like `AUDIT_BACKEND`), and the
Public Service swaps backends without code changes.

### Why the Grid exists

So that every Public Service has the same shape for the same problems
— and so a Permits-team developer can read a Parking-team incident
report and immediately know what "audit log" means there. Plus, every
Public Service is portable: the adapter pattern means a city can run
Parking on Postgres+local-disk on a $20/mo VPS *or* on RDS+S3+SES on
AWS, with the same code.

### The six Grid services

| Service | What it does | Default adapter | Contract format |
|---|---|---|---|
| `identity` | Who is making this request? | `NoAuthAdapter` (dev) | JSON Schema |
| `payments` | Resident → city money movement | `LogOnlyPaymentsAdapter` | OpenAPI 3.1 |
| `notifications` | Email/SMS/push to a recipient | `LogOnlyAdapter` | OpenAPI 3.1 |
| `audit` | Append-only log of state changes | `PostgresAuditAdapter` (real) | JSON Schema |
| `document_storage` | PUT/GET/DELETE on opaque keys | `LocalFilesystemAdapter` | OpenAPI 3.1 |
| `accessibility` | WCAG violation records | `InMemoryAccessibilityAdapter` | JSON Schema |

Specs: `blueprint/grid/<service>/contract.yaml`. Default adapters:
`blueprint/template/{{cookiecutter.public_service_name}}/libraries/grid_adapters/grid_adapters/<service>/`.

### Grid vs Contract

These are easy to confuse because both involve YAML schemas.

- A **Contract** is one Public Service's promise to other Public
  Services. (Parking → Permits.)
- A **Grid contract** is the standard a Public Service must implement
  *internally* for one of the six backbone capabilities. (Every
  Public Service must conform to the `audit` Grid contract; nothing
  external sees it.)

If you're choosing how Parking talks to Permits → that's a Contract.
If you're choosing how Parking implements its audit log → that's the
Grid.

## The blueprint

### blueprint

This repo (`PublicStackOrg/blueprint`). The **template** every Public
Service is generated from, plus the **format spec** for Contracts and
the **contracts** for the Grid services.

A Public Service is generated *from* `blueprint` and then evolves
independently. `blueprint` is not a runtime dependency; nothing in a
Public Service imports it after generation. Upgrades happen by
running `publicstack upgrade --to <version>` (when implemented),
which applies version-specific migration scripts.

### `publicstack` CLI

A Python CLI (in `blueprint/cli/`) that runs `cookiecutter` against
`blueprint/template/` plus convenience commands:

- `publicstack new service <name>` — generate a new Public Service
- `publicstack add api/app/contract/grid <name>` — scaffold pieces
  inside an existing Public Service
- `publicstack doctor` — toolchain health check
- `publicstack upgrade --to <v>` — migrate to a newer blueprint
  version (stub for now)
- `publicstack lint` — run the compliance suite (stub until Phase 5)

### `publicstack-contracts` CLI

Standalone Python CLI at `blueprint/contracts/tooling/`. Two
commands:

- `publicstack-contracts validate <path>` — is this contract
  well-formed?
- `publicstack-contracts diff <old> <new>` — does the new version
  break back-compat with the old one?

The Phase 5 compliance suite imports it as a library.

### Compliance suite (Phase 5, planned)

Tests every Public Service against PublicStack standards: every
entity has a working data-export endpoint, every Contract validates,
every Grid service has a configured adapter, accessibility checks
pass on Flutter web builds, observability fields are present, etc.

Lives in `blueprint/compliance/`. The `publicstack lint` command
will invoke it.

## Versioning

### Contract version

Major-only (`v1`, `v2`). New optional fields, new endpoints, new
enum values, relaxed constraints → same major. Anything breaking →
new major. There is no `v1.1`. See
`blueprint/contracts/README.md`.

### Blueprint version

Stored in `blueprint/VERSION`. Each generated Public Service
records the blueprint version it came from in `BLUEPRINT_VERSION`.
Migration guides between versions live in
`blueprint/docs/migration-guides/`.

## Vocabulary that is *not* PublicStack vocabulary

- **"Block"** — old name for Public Service. Don't use.
- **"PublicStack-Grid server"** / **"the Grid host"** — there is no
  such thing. The Grid is local to each Public Service.
- **"Grid service"** — fine in conversation, but mean it: a service
  that conforms to one of the six Grid contracts, *implemented
  inside a Public Service*.
- **"Microservice"** — fine; usually we say "internal service" or
  "backend service" to disambiguate from "Public Service".
- **"App"** — always a Flutter app under `apps/`. Never the Public
  Service as a whole.

## See also

- [`PLAN.md`](./PLAN.md) — the phased plan for building the
  ecosystem.
- [`SPIKES.md`](./SPIKES.md) — known hard problems (identity
  provider choice, payments execution, multi-tenancy, audit
  immutability, etc.).
- `blueprint/contracts/README.md` — the Contract format spec.
- `blueprint/grid/README.md` — the six Grid services.
- `blueprint/cli/README.md` — the `publicstack` CLI.
