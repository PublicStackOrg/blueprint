# {{ cookiecutter.public_service_name }} — Claude Code context

This file is the per-Public-Service Claude context for
**{{ cookiecutter.public_service_name }}**. It layers on top of the
org-wide `CLAUDE.md` one directory up.

## What this is

{{ cookiecutter.description }}

Generated from [`PublicStackOrg/blueprint`](https://github.com/PublicStackOrg/blueprint)
v{{ cookiecutter.blueprint_version }} (see `BLUEPRINT_VERSION`). Each
PublicStack Public Service is its own monorepo, its own AGPL-3.0 repo,
and operationally independent of every other Public Service. They talk
to each other only through Contracts.

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
- **Frontends:** Flutter 3.41+ + Dart 3.x + Riverpod + GoRouter +
  shared `libraries/ui` design system.
- **Monorepo tooling:** NX 22+ with `@nxlv/python` plugin + Poetry.
- **Mandatory dependencies:** Postgres 16, Redis.
- **Observability:** Prometheus `/metrics`, OpenTelemetry tracing
  (FastAPIInstrumentor), structured JSON logging via
  python-json-logger. The compliance suite enforces all three.
- **Security middleware:** `Content-Security-Policy: default-src 'self'`
  on every response; `HTTPSRedirectMiddleware` outside local dev.
- **Optional / pluggable:** queue (RQ default), object storage
  (local-fs default; S3/GCS/R2 via adapter), identity (no-auth dev
  stub default; real impl per blueprint's `docs/SPIKES.md`).

## Conventions

- **AGPL-3.0 short header on every source file.** The generator seeded
  these — keep them when refactoring.
- **Every entity has a working data-export endpoint.** The compliance
  suite (Phase 5 of blueprint) enforces it. Don't add a model without
  an export route.
- **Observability is mandatory.** Structured logs with the required
  fields, Prometheus `/metrics`, OpenTelemetry tracing.
- **Default to no comments.** Code explains *what*; comments explain
  *why* — and only when *why* is non-obvious.
- **Don't add abstractions for hypothetical callers.** Three real
  callers, then a helper.
- **Tests hit a real Postgres** — never a mocked DB. The compose
  service container is the test database.

## Identity (today)

This service runs in **no-auth dev mode** by default
(`AUTH_MODE=none`). `get_current_user()` returns a hardcoded test user
so the API is runnable without any identity provider. A real Grid
identity adapter slots in via env var when blueprint Phase 4 ships;
until then, don't write tests that assume real-auth behaviour.

## Self-healing context

When you notice something that would have helped you (or future-you)
work better — a non-obvious convention, a repeated workflow, a
permission prompt that recurs, a tool you keep re-discovering —
capture or propose it.

- **{{ cookiecutter.public_service_name }}-specific convention** →
  edit this file.
- **Org-wide convention** → propose an edit to the workspace-root
  `CLAUDE.md`.
- **Convention that should ship to every future Public Service** →
  propose an edit to `blueprint`'s template CLAUDE.md.
- **Repeated automated behavior** → propose a hook in
  `.claude/settings.json`.
- **Repeated multi-step workflow** → propose a slash command in
  `.claude/commands/` or a skill in `.claude/skills/`.

Always *propose* before editing shared org config.

## Pointers

- **`blueprint`:** <https://github.com/PublicStackOrg/blueprint>. The
  template this Public Service was generated from.
- **`BLUEPRINT_VERSION`:** at the repo root. Tells you which version
  of `blueprint` you're on. Upgrade with `publicstack upgrade --to <version>` once the CLI ships.
- **`docs/PLAN.md` in `blueprint`:** the phased plan for the whole
  ecosystem.
- **`docs/SPIKES.md` in `blueprint`:** known hard problems (identity,
  payments execution, multi-tenancy, FOIA, audit immutability, hosting
  cost). If you're touching one of those areas, read the spike first.
