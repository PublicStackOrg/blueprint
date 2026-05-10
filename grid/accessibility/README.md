# Grid accessibility

Server-side primitives for recording WCAG 2.2 AA violations from automated
scans of every generated Flutter app.

Flutter-side helpers (semantic labels, focus management, contrast) live in
`libraries/ui/`, not in this Grid service.

## Contract

[`contract.yaml`](./contract.yaml) — JSON Schema 2020-12 for an
`A11yViolation` and a `A11yScanReport` (a list of violations).

## Default adapter

`InMemoryAccessibilityAdapter` accepts violation records and exposes them via
a debug endpoint. The Phase 5 compliance suite scrapes this endpoint after
running axe-core against each app's web build.

## Why thin

SPIKES.md #4 leaves room for a stack rethink if Flutter web a11y can't pass.
Keeping the contract narrow (just record-and-query violations) means a
fallback to plain-web for staff/kiosk apps doesn't bump the contract.

## Env vars

- `ACCESSIBILITY_BACKEND` — `in_memory` (default).

## Out of scope for v1

- Long-term storage of historical scan reports (cities can wire to their own
  observability stack).
- Flutter-runtime instrumentation (lives in `libraries/ui/`).
