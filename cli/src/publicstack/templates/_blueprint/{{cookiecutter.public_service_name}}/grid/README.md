# `grid/`

Per-Grid-service configuration for **{{ cookiecutter.public_service_name }}**.
Each file declares which Grid contracts this Public Service uses and how
to wire them.

Filled in during **Phase 4** of `blueprint`'s plan. Expected files:

- `identity.yaml` — what auth this PS needs.
- `payments.yaml` — payment processor wiring (city-direct).
- `notifications.yaml` — channels and templates.
- `audit.yaml` — audit log destination.

The Grid is a contract layer, not a deployed shared service. Each
Public Service implements Grid contracts locally via adapters in
`libraries/grid_adapters/`.
