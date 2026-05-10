# Grid payments

Resident-to-city money movement, via the city's chosen processor.

PublicStack is never merchant of record. The Public Service creates an
intent, the adapter hands the resident off to a hosted page (Stripe,
local-bank, city-merchant), the resident pays the city. Card data
never touches PublicStack code.

## Contract

[`contract.yaml`](./contract.yaml) — OpenAPI 3.1. Three operations:
`POST /intents`, `GET /intents/{id}`, `POST /intents/{id}/refund`.

## Default adapter

`LogOnlyPaymentsAdapter` records intents in memory and returns a fake
`redirect_url`. Useful for local dev and tests; never moves money.

## Provider adapters (planned)

Stripe, local-bank, city-merchant. Each must serve the OpenAPI surface
in `contract.yaml`. Processor-specific fields live in `metadata` —
that's the seam SPIKES.md #1 leaves open.

## Env vars

- `PAYMENTS_BACKEND` — `log_only` (dev), `stripe`, `local_bank`, …
- Provider-specific keys (`STRIPE_API_KEY`, etc.) per adapter.

## Out of scope for v1

- City-billing flow (PublicStack invoicing cities for hosting). Separate
  pipeline; not part of this contract.
