# Contracts — format spec

A **Contract** is a versioned schema one Public Service exposes to
others, or consumes from them. Contracts are how Parking, Permits, 311,
and any other Public Service stay interoperable without runtime
coupling.

This directory holds:

- This file — the **format spec**: what a contract definition must look
  like, how versioning works, what counts as a breaking change.
- `examples/` — canonical exemplars referenceable from any Public
  Service.
- `tooling/` — the `publicstack-contracts` Python package: validates
  contract files and detects breaking changes between versions. The
  Phase 5 compliance suite imports it as a library.

Per-Public-Service contracts (the ones a specific Public Service
*exposes* or *consumes*) live in that Public Service's own
`contracts/exposed/` and `contracts/consumed/` directories — not here.

## Two formats

PublicStack admits two contract formats. Pick whichever fits the shape
of the thing you're contracting.

**OpenAPI 3.1 (YAML)** — for HTTP-shaped contracts: Parking exposes a
`citations.v1` REST API; Permits consumes it. Use OpenAPI when
endpoints, parameters, and responses are the real surface.

**JSON Schema (Draft 2020-12, YAML or JSON)** — for non-HTTP shapes:
data records, event payloads, claim sets. Use JSON Schema when the
"contract" is the *shape* of a value — an audit log entry, an identity
token's claims — and the transport is whatever moves it.

The tooling detects format **by content**, not filename:

- Top-level `openapi:` field present → OpenAPI 3.1.
- `$schema:` present (referencing 2020-12), or top-level `type:` /
  `properties:` / `$defs:` → JSON Schema.
- Both present, or neither → error. Disambiguate before re-running.

## Directory layout

```
blueprint/contracts/
├── README.md             # this file
├── examples/             # canonical exemplars
└── tooling/              # publicstack-contracts package

<public-service>/contracts/
├── exposed/              # this Public Service's contracts (owned)
│   └── citations.v1.yaml
└── consumed/             # contracts depended on (pinned copies)
    └── permits.identity.v1.yaml
```

`exposed/` is owned by the Public Service. `consumed/` is a pinned copy
of someone else's `exposed/<x>.<v>.yaml` — when the producer ships a
new version, the consumer re-pins by copying the new file and updating
its code. A consumed file must byte-match an `exposed/` file somewhere;
the compliance suite checks this in Phase 5.

## File naming

`<name>.<version>.yaml` (or `.json`).

- `<name>` matches `[a-z][a-z0-9_-]{1,49}`. Match the `<name>` to the
  *concept*, not the producer (`citations` not `parking-citations` —
  the `parking/` part is implicit from the Public Service that owns
  it).
- `<version>` matches `^v[0-9]+$`. Major-only — see versioning below.

Examples: `citations.v1.yaml`, `audit_entry.v3.yaml`,
`identity_token.v1.yaml`.

For consumed contracts that name another Public Service, use
`<producer>.<name>.<version>.yaml`: `permits.identity.v1.yaml`.

## Required metadata

**OpenAPI 3.1:**

```yaml
openapi: 3.1.0
info:
  title: citations            # matches <name>
  version: v1                 # matches <version>
  description: |
    What this contract is for, who exposes it, who's expected to consume it.
  x-publicstack-contract-name: citations
  x-publicstack-contract-version: v1
paths: {}
components:
  schemas: {}
```

**JSON Schema (Draft 2020-12):**

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://contracts.publicstack.org/audit_entry.v1.json
title: audit_entry
description: |
  An append-only audit log entry. See blueprint/grid/audit/README.md.
x-publicstack-contract-name: audit_entry
x-publicstack-contract-version: v1
type: object
properties: { ... }
required: [ ... ]
```

The `x-publicstack-contract-{name,version}` extensions are how tooling
cross-checks the filename against the contents. Keep them in sync.

## Versioning

**Major-only.** Versions exist for compat boundaries, not changelog
entries.

- A new optional field, a new endpoint, a new enum value, a relaxed
  constraint → **same major**. Bump the file's contents; keep `v1`.
- A breaking change → **new major**. `citations.v2.yaml` lives next to
  `citations.v1.yaml`. The producer ships both for a deprecation
  window; the consumer migrates when it's ready.

There is no `v1.1` or `v1.0.3`. If you'd reach for one, you're probably
holding a changelog and should write a `CHANGELOG.md` for the
contract instead.

## Breaking-change rules

A change is **breaking** if it would cause a previously-correct
consumer of the older version to fail against the newer one. The
tooling flags these as exit-code-1 findings:

| Rule | Description | Severity |
|---|---|---|
| `JS001` | Removed a required property | breaking |
| `JS002` | Added a required property without a `default` | breaking |
| `JS003` | Type narrowed (`integer→number` is the only whitelisted widening) | breaking |
| `JS004` | Removed an enum value | breaking |
| `JS005` | Tightened a constraint (`maxLength` shrunk, `pattern` more restrictive, `exclusiveMaximum` lowered, `minLength` raised) | breaking |
| `JS006` | Added an optional property | info |
| `JS007` | Added an enum value | info |
| `JS008` | Loosened a constraint | info |

OpenAPI contracts apply the same set, mapped through OAS-equivalent
shapes (path/method removal = `JS001`-class; response schema
narrowing = `JS003`/`JS005`; etc.). When `oasdiff` is on PATH,
`publicstack-contracts diff` prefers it for richer OpenAPI semantic
checks; when it's not, the pure-Python fallback covers the same rule
set above.

A few semantics worth calling out:

- **Enum removal is breaking, full stop.** PublicStack treats every
  contract as producer-owned: the consumer has narrowed types around
  the values it sees; removing a value is a type-narrowing on their
  side regardless of whether the value was used in requests or
  responses.
- **Added-required-with-`default` is OK.** Rule `JS002` special-cases
  `default:` presence. If old consumers omit the field, the default
  fills in and behavior is preserved.
- **Type widening** is generally breaking. Only `integer → number` is
  whitelisted. `string → [string, null]` changes the cardinality
  contract; `string → [string, integer]` breaks consumer type
  narrowing.

## Deprecation

Mark a field, parameter, or path with `deprecated: true` in version
`vN`. The next major (`vN+1`) is allowed to remove it. The tooling
warns when consumed contracts still reference deprecated elements,
giving the consumer a heads-up before the producer cuts the next
version.

## Tooling

Install via pipx (the workspace `install.sh` does this automatically
when a sibling `blueprint/contracts/tooling/` directory is present):

```bash
pipx install ./blueprint/contracts/tooling
```

Two subcommands:

```bash
publicstack-contracts validate <path>       # exit 0 valid, 1 invalid, 2 unparseable
publicstack-contracts diff <old> <new>      # exit 0 no breaking, 1 breaking, 2 tool error
```

`validate` checks the file is well-formed against its detected format
(OpenAPI 3.1 or JSON Schema 2020-12). `diff` walks both sides and
reports findings keyed by the rule IDs above.

For full OpenAPI semantic diff coverage, install `oasdiff` separately
(`brew install oasdiff` or download from its GitHub releases). The
tooling falls back gracefully when it's missing.

## See also

- `examples/audit_entry.v1.yaml` — JSON Schema exemplar.
- `examples/identity_token.v1.yaml` — JSON Schema exemplar.
- `examples/citations.v1.yaml` — OpenAPI 3.1 exemplar (Parking →
  Permits).
- `examples/permits.identity.v1.yaml` — cross-Public-Service consumed
  contract example.
- `blueprint/grid/<service>/contract.yaml` — every Grid service ships
  a contract using this format.
