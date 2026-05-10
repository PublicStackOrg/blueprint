# Grid document_storage

Object storage: PUT/GET/DELETE/LIST on opaque keys.

## Contract

[`contract.yaml`](./contract.yaml) — OpenAPI 3.1.

## Default adapter

`LocalFilesystemAdapter` writes to a configurable directory on disk. Useful
for dev and small-city single-VPS deploys.

## Provider adapters (planned)

S3, GCS, R2, Azure Blob, MinIO. Each must serve the OpenAPI surface and
return `etag` values stable across reads.

## Env vars

- `DOCUMENT_STORAGE_BACKEND` — `local` (dev), `s3`, `gcs`, `r2`, …
- `DOCUMENT_STORAGE_LOCAL_ROOT` — directory for the local adapter.
- Provider-specific creds per adapter.

## Note on naming

This service was previously named `storage` in v0.1.0 of the template. As of
blueprint v0.2.0 it is `document_storage`, matching PLAN.md §1's vocabulary.
See `blueprint/docs/migration-guides/v0.1_to_v0.2.md` for upgrade notes.
