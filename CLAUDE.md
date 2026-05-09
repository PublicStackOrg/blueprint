# Public Service — Claude Code context

This file ships at the root of every Public Service generated from
`blueprint`. It is the per-service Claude context: conventions specific
to a single Public Service, layered on top of the org-wide
`CLAUDE.md` one directory up.

> **For maintainers of `blueprint` itself:** this is the *starter*
> file. When a Public Service is generated, this file is copied into
> its repo and the generated service edits it freely. Don't put
> `blueprint`-internal notes here.

## What this Public Service is

A single PublicStack Public Service — a deployable civic application
(Parking, Permits, 311, …). Generated from `blueprint`; the version it
was generated from is recorded in `BLUEPRINT_VERSION`.

Each Public Service is its own monorepo, its own AGPL-3.0 repo, and
operationally independent of every other Public Service. They talk to
each other only through Contracts.

## Vocabulary

| Term | Meaning |
|---|---|
| **Public Service** | This whole repo — one deployable civic application. |
| **internal service** / **backend service** | A microservice inside this repo. Lives under `services/`. |
| **app** / **frontend** | A Flutter app under `apps/`. |
| **library** | A shared Python or Dart package under `libraries/`. |
| **Contract** | A versioned schema this Public Service exposes (`contracts/exposed/`) or consumes (`contracts/consumed/`). |
| **Grid** | Shared backbone (identity, payments, notifications, audit, document storage, accessibility). Consumed via adapters in `libraries/grid_adapters/`. The Grid is a contract layer, not a deployed shared service. |

## Stack

- **Backend:** Python 3.13 + FastAPI + SQLAlchemy 2.0 async + Alembic.
- **Frontends:** Flutter 3.41+ + Dart 3.x + Riverpod + GoRouter + the
  shared `libraries/ui` design system.
- **Monorepo tooling:** NX 22+ with `@nxlv/python` plugin + Poetry.
- **Mandatory dependencies:** Postgres 16, Redis.
- **Optional / pluggable:** queue (RQ default; Celery+SQS/Cloud Tasks
  via adapter), object storage (MinIO default; S3/GCS/R2 via adapter),
  identity (TBD per `blueprint`'s `docs/SPIKES.md`).

## Conventions

- **AGPL-3.0 header on every source file.** The generator seeds these;
  keep them when refactoring.
- **Every entity has a working data-export endpoint.** This is a
  non-negotiable — the compliance suite enforces it.
- **Observability is mandatory.** Structured logs with the required
  fields, Prometheus `/metrics`, OpenTelemetry tracing.
- **Default to no comments.** Code explains *what*; comments explain
  *why* — only when *why* is non-obvious.
- **Don't add abstractions for hypothetical callers.** Three real
  callers, then a helper.
- **Tests hit a real Postgres** — never a mocked DB.

## Self-healing context

When you notice something that would have helped you (or future-you)
work better — a non-obvious convention, a repeated manual workflow, a
permission prompt that keeps recurring, a tool you keep
re-discovering — capture or propose it.

- **Public-Service convention** → propose an edit to this file.
- **Org-wide convention or insight** → propose an edit to the
  workspace-root `CLAUDE.md` (one directory up).
- **Convention that should be copied into every future Public
  Service** → propose an edit to `blueprint/CLAUDE.md` upstream.
- **Repeated automated behavior** → propose a hook in
  `.claude/settings.json`.
- **Repeated multi-step workflow** → propose a slash command in
  `.claude/commands/` or a skill in `.claude/skills/`.

Always *propose* before editing shared org config.

## Pointers

- **`blueprint`** — `https://github.com/PublicStackOrg/blueprint`. The
  template this Public Service was generated from. Upgrade with
  `publicstack upgrade --to <version>`.
- **`BLUEPRINT_VERSION`** — at the repo root. Tells you which version
  of `blueprint` you're on.
- **`docs/PLAN.md`** in `blueprint` — the phased plan for the whole
  ecosystem.
- **`docs/SPIKES.md`** in `blueprint` — known hard problems
  (identity, payments execution, multi-tenancy, FOIA, audit
  immutability, hosting cost). If you're touching one of those areas,
  read the spike first.
