# SPDX-License-Identifier: AGPL-3.0-or-later
"""Grid adapters — pluggable backends for shared services.

Each subpackage defines an interface (Protocol or ABC) plus a default
implementation. Public Services consume the interface; deployments swap
the implementation via env var without touching service code.

Phase 2 ships interface + a single default impl per adapter:

- queue: RQ on Redis (default).
- storage: local filesystem (default).
- identity: no-auth dev stub (returns a hardcoded test user).
- notifications: log-only no-op (default).

Real implementations (Stripe / S3 / Keycloak / SendGrid / etc.) land in
Phase 4 once the Grid contract specs are settled.
"""
