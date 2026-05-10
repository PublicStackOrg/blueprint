# `grid/`

The blueprint-defined Grid contracts — the abstract shape of every shared
backbone service that Public Services consume.

The Grid is a **contract layer, not a deployed shared service.** Each
Public Service implements Grid contracts locally via adapters in its own
`libraries/grid_adapters/`. Public Services do not call out to a
centrally-deployed PublicStack-Grid instance — that keeps every Public
Service portable and self-hostable.

## Six services, one subdirectory each

Each subdirectory ships a `contract.yaml` (OpenAPI 3.1 or JSON Schema 2020-12)
and a `README.md` describing the default adapter and provider plug-ins.

| Service | Format | Default | Notes |
|---|---|---|---|
| [`identity/`](./identity/) | JSON Schema | `NoAuthAdapter` (dev) | Token-claims shape. SPIKES.md #2 leaves the default self-hostable provider open. |
| [`payments/`](./payments/) | OpenAPI 3.1 | `LogOnlyPaymentsAdapter` | City-direct flow; PublicStack is never merchant of record. SPIKES.md #1 details. |
| [`notifications/`](./notifications/) | OpenAPI 3.1 | `LogOnlyAdapter` | Email/SMS/push send + status. |
| [`audit/`](./audit/) | JSON Schema | `PostgresAuditAdapter` | Append-only with hash-chain ready. SPIKES.md #6 details. |
| [`document_storage/`](./document_storage/) | OpenAPI 3.1 | `LocalFilesystemAdapter` | Object PUT/GET/DELETE/LIST. |
| [`accessibility/`](./accessibility/) | JSON Schema | `InMemoryAccessibilityAdapter` | A11y violation records; SPIKES.md #4 keeps the contract thin. |

## Validating a Grid contract

```bash
publicstack-contracts validate blueprint/grid/identity/contract.yaml
publicstack-contracts diff blueprint/grid/identity/contract.yaml \
                            blueprint/grid/identity/contract.v2.yaml
```

## Wiring a Grid service into a Public Service

```bash
cd <my-public-service>
publicstack add grid identity     # writes grid/identity.yaml + adapter stub
```

See `blueprint/cli/` for the command implementation.
