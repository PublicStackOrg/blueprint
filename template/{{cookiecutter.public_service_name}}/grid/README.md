# `grid/`

Per-Grid-service configuration for **{{ cookiecutter.public_service_name }}**.
Each file declares which Grid contracts this Public Service uses and how to
wire them.

The Grid is a contract layer, not a deployed shared service. Each Public
Service implements Grid contracts locally via adapters in
`libraries/grid_adapters/`. The contracts themselves live upstream at
`blueprint/grid/<service>/contract.yaml`.

## Files

- `identity.yaml` — what auth this PS needs.
- `payments.yaml` — payment processor wiring (city-direct).
- `notifications.yaml` — channels and templates.
- `audit.yaml` — audit log destination.
- `document_storage.yaml` — object-storage backend.
- `accessibility.yaml` — a11y scan storage.

Add or update with `publicstack add grid <service>` (idempotent).
