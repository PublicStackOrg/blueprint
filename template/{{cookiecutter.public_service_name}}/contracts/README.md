# `contracts/`

Contracts this Public Service exposes to and consumes from other
PublicStack services.

- `exposed/` — Contracts **{{ cookiecutter.public_service_name }}**
  publishes. Each is a versioned schema file (e.g.,
  `<topic>.v1.yaml`).
- `consumed/` — Contracts this service depends on from other Public
  Services. Each file references a remote Contract by name + version.

Filled in during **Phase 4** of `blueprint`'s plan, when the Contract
format spec lands. The compliance suite enforces back-compat rules.
