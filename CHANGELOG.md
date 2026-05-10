# Changelog

All notable changes to `blueprint` will be documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
`blueprint` uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
— Public Services declare which `blueprint` version they were generated
from in their `BLUEPRINT_VERSION` file.

## [Unreleased]

## [0.3.0] — 2026-05-10

### Added

- **Compliance suite** (`publicstack-compliance`) at `compliance/`,
  pipx-installable. Six checks — `data_export`, `contract_compat`,
  `grid_integration`, `security`, `observability`, `accessibility`
  (Phase 5 §6 of `docs/PLAN.md`). Rules are id-tagged
  (`DEX-001`/`CTR-001`/`GRD-001`/`SEC-001`/`OBS-001`/`A11Y-001`)
  with severity `breaking | warn | info` and exit codes 0/1/2.
- Template ships **compliant by default**: every freshly-generated PS
  exits 0 on `publicstack-compliance run`. Specifically:
  - `services/api/api/main.py` — CSP middleware, HTTPSRedirectMiddleware
    (env-gated), JsonFormatter (python-json-logger),
    `FastAPIInstrumentor` (OpenTelemetry).
  - `services/api/api/config.py` — new `environment` setting.
  - `services/api/api/routers/v1/export_router.py` — NDJSON streaming
    `/export/items` endpoint.
  - `services/api/tests/test_export.py` — integration test for the
    export endpoint.
  - `services/api/tests/conftest.py` — `OTEL_SDK_DISABLED=true` so
    OpenTelemetry's default exporter doesn't pollute pytest output.
  - `services/api/pyproject.toml` — adds `opentelemetry-sdk`,
    `opentelemetry-instrumentation-fastapi`,
    `opentelemetry-exporter-otlp`, `python-json-logger`.
  - `services/api/api/dependencies.py` — `get_storage_adapter` →
    `get_document_storage_adapter` rename (matches Grid service name).

### Changed

- `publicstack lint` (in the `publicstack` CLI) is no longer a stub —
  delegates via `subprocess` to `publicstack-compliance run`.

## [0.2.0] — 2026-05-10

### Added

- Contract format spec at `contracts/README.md` — OpenAPI 3.1 + JSON
  Schema (Draft 2020-12) supported, format-detected by content. Eight
  back-compat rules `JS001`–`JS008` documented.
- Four exemplar contracts under `contracts/examples/`.
- `publicstack-contracts` CLI (`contracts/tooling/`): `validate`,
  `diff`, `version`. Pipx-installable.
- Six Grid contract specs under `grid/<service>/{contract.yaml,
  README.md}`.
- Per-PS Grid adapter slots for `payments`, `audit`, `accessibility`.
  Real `PostgresAuditAdapter` with hash-chain ready entries; new
  Alembic migration `0002_audit_log`.
- `publicstack add grid <service>` — bundled cookiecutter; idempotent.
- First migration guide at `docs/migration-guides/v0.1_to_v0.2.md`.

### Changed

- Renamed Grid `storage` to `document_storage` to align with the
  PLAN.md §1 vocabulary.

## [0.1.0] — 2026-05-09

### Added

- Cookiecutter template tree under `template/` that generates a
  complete Public Service monorepo:
  - **Backend:** FastAPI api with `/health`, `/version`, `/metrics`,
    and a CRUD example for a placeholder `Item` entity. RQ-based
    worker. Alembic migrator with initial migration.
  - **Libraries:** `core` (DB/config/error types), `grid_adapters`
    (queue/storage/identity/notifications interfaces with default
    impls), `test_helper` (pytest fixtures), `ui` (Flutter design
    system, sealed `AppEvent` bus, Dio-backed `ApiClient`, a11y
    helpers).
  - **Apps:** `resident` (mobile + web), `staff` (web), `kiosk`
    (web). Each renders a working home screen and calls the API.
  - **Dev loop:** `docker-compose.yml` (postgres + redis + migrator
    + api + worker), `docker-compose.e2e.yml`, scripts (`dev.sh`,
    `dev-down.sh`, `reset-db.sh`, `flutter-run.sh`).
  - **CI:** `.github/workflows/ci.yml` running Python lint + tests
    against real Postgres + Redis service containers, Flutter
    analyze + test, Flutter web release builds, Docker image
    builds, and a `no-silent-catch` Dart guard.
- `blueprint/.github/workflows/ci.yml` validating the template
  renders cleanly and the generated PS's Python + Flutter test
  suites pass on every PR.
- Identity ships as a no-auth dev stub (`AUTH_MODE=none`) returning a
  hardcoded test user. Real Grid identity adapter slots in at Phase 4.

## [0.0.1] — 2026-05-09

### Added

- Initial repo skeleton: top-level legal/governance docs (LICENSE,
  LICENSING.md, CODE_OF_CONDUCT.md, SECURITY.md, CONTRIBUTING.md,
  GOVERNANCE.md), README, per-service starter CLAUDE.md, VERSION,
  CHANGELOG.
- Empty placeholder directories for `template/`, `compliance/`, `cli/`,
  `contracts/`, `grid/`, `docs/`, each with a stub README pointing at
  the phase that fills it in.
- `docs/PLAN.md` and `docs/SPIKES.md` migrated from the workspace root.

This release ships no executable code. Phase 2 of `docs/PLAN.md` will
populate the template tree.
