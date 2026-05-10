# Grid notifications

Outbound email, SMS, and push messages.

## Contract

[`contract.yaml`](./contract.yaml) — OpenAPI 3.1. `POST /messages` to queue,
`GET /messages/{id}` for delivery status.

## Default adapter

`LogOnlyAdapter` writes to stdout and never sends. Useful for dev and tests.

## Provider adapters (planned)

- Email: SES, Postmark, SMTP-direct
- SMS: Twilio, AWS SNS
- Push: FCM, APNs

Each must serve the contract surface and return a `Message` whose `status`
reflects best-effort observed delivery state.

## Env vars

- `NOTIFICATIONS_BACKEND` — `log_only` (dev), `ses`, `twilio`, …
- Provider-specific credentials per adapter.

## Out of scope for v1

- Per-recipient suppression lists (deferred; cities handle via the provider's
  console for v1).
- In-app notification feed (separate concern; lives inside each Public
  Service rather than the Grid).
