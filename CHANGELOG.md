# Changelog

All notable changes to `blueprint` will be documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
`blueprint` uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
— Public Services declare which `blueprint` version they were generated
from in their `BLUEPRINT_VERSION` file.

## [Unreleased]

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
