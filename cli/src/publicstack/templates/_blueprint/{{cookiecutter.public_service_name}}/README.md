# {{ cookiecutter.public_service_name }}

{{ cookiecutter.description }}

A PublicStack Public Service generated from
[`PublicStackOrg/blueprint`](https://github.com/PublicStackOrg/blueprint)
v{{ cookiecutter.blueprint_version }}.

## Quick start

```bash
npm install        # NX + JS dev tooling
poetry install     # Python deps for every service + library
./scripts/dev.sh   # postgres + redis + api + worker via Docker Compose
```

Then:

- API: `curl localhost:8000/health` → `{"status":"ok"}`
- Resident app: `cd apps/resident && flutter run -d chrome --web-port 3000`
- Staff dashboard: `cd apps/staff && flutter run -d chrome --web-port 3001`
- Kiosk: `cd apps/kiosk && flutter run -d chrome --web-port 3002`

## Layout

```
{{ cookiecutter.public_service_name }}/
├── apps/             Flutter apps (resident, staff, kiosk)
├── services/         Python services (api, worker, migrator)
├── libraries/        shared Python + Dart packages
├── contracts/        Contracts this PS exposes/consumes (Phase 4)
├── grid/             Grid integration configs (Phase 4)
├── exports/          required data export endpoints (Phase 5)
├── deploy/           docker-compose, helm chart, terraform (Phase 6)
├── docs/             operator + resident docs, API docs
├── tests/            cross-service tests, compliance suite
├── scripts/          dev-loop helpers
└── tools/            CI grep guards
```

## Working on it

- **Code conventions:** see [`CLAUDE.md`](./CLAUDE.md).
- **Generated from blueprint:** see
  [`BLUEPRINT_VERSION`](./BLUEPRINT_VERSION) for the version this tree
  was scaffolded from. Upgrade with `publicstack upgrade --to <version>`
  once the CLI ships (Phase 3).
- **Self-hosting:** see `deploy/HOSTING.md` for VPS / Helm / Terraform
  recipes once Phase 6 lands.

## License

[AGPL-3.0](./LICENSE) — the org-wide default for every PublicStack
repo. See [`LICENSING.md`](./LICENSING.md) for why.

## Status

Generated from blueprint v{{ cookiecutter.blueprint_version }}. Phase 2
of blueprint's plan only ships the runnable scaffolding — Contracts,
Grid wiring, the compliance suite, and the deployment story all land in
later phases.
