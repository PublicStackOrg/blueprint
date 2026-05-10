# Grid identity

Authentication and identity claims, normalized.

## Contract

[`contract.yaml`](./contract.yaml) — JSON Schema 2020-12 for the token-claims
shape every `IdentityAdapter` must surface. See `blueprint/contracts/README.md`
for the format spec.

## Default adapter

`libraries/grid_adapters/grid_adapters/identity/NoAuthAdapter` returns a
hardcoded dev user when `AUTH_MODE=none` (the dev default). It exists so
Public Services run end-to-end without an external identity provider.

## Provider adapters (planned)

SPIKES.md #2 leaves the default self-hostable provider unresolved. Adapters
for Keycloak, ZITADEL, Authentik, Auth0, Clerk, Cognito will land as that
decision matures. Each must produce claims that conform to `contract.yaml`.

## Env vars

- `AUTH_MODE` — `none` (dev), `keycloak`, `zitadel`, … (TBD per spike)
- Provider-specific vars — defined by each adapter; documented in its README.

## Compliance check

Phase 5's compliance suite verifies that any non-`none` `AUTH_MODE` resolves
to an adapter that produces conformant claims.
