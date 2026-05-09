# SPIKES — hard problems for PublicStack

Problems we know are hard and that need real thinking before we hit them.
Sibling of `PLAN.md`. Migrates to `blueprint/docs/SPIKES.md` once Phase 1
of PLAN.md ships.

Each entry follows the same shape:

- **Problem** — what's hard
- **Why it matters** — what breaks if we get it wrong
- **What we know** — decisions / constraints already in place
- **What we don't know** — the specific unknowns
- **When we need to resolve** — which Phase / which Public Service forces
  the decision

When an entry resolves, replace its body with a one-line link to the PR /
RFC / commit that closed it.

---

## 1. Payments execution

- **Problem.** The payments *model* is decided (city-direct: PublicStack
  never touches funds; cities bring their own processor; residents pay
  the city; we invoice cities for hosting). The *execution* is not.
- **Why it matters.** Payments is where money lives. Get the contract
  shape wrong and every Public Service that takes money has to be
  rewritten. Get our own billing wrong and we don't get paid.
- **What we know.** City-direct flow. Stripe / local-bank / city-merchant
  processors are all in scope. We want to never be merchant of record.
- **What we don't know.**
  - The Grid `payments` contract shape — what does a Public Service hand
    to the adapter, what comes back?
  - What transaction state does a Public Service record locally even
    though it doesn't move money (audit, dispute trail, refund hooks)?
  - How do we bill cities for hosting (Stripe Billing? Invoice/wire?
    Annual contracts?) — separate flow from resident-to-city money.
  - Refunds, disputes, chargebacks — what's the Public Service's role?
  - PCI scope: does the Public Service ever see card data, or always
    redirect to a hosted page?
- **When we need to resolve.** Before any Public Service that takes
  payments ships. Parking is the forcing function (Phase 8).

## 2. Identity provider

- **Problem.** No default identity provider chosen. Every Public Service
  needs auth.
- **Why it matters.** Identity is in the critical path of every request.
  Wrong choice means either AGPL incompatibility (Auth0/Clerk/Cognito
  managed-only), bad self-host ergonomics (Keycloak is heavy), or weak
  feature set.
- **What we know.** The Grid pattern is settled: identity is a contract
  in `grid/identity/`, with adapter implementations in
  `libraries/grid_adapters/identity/`. Public Services depend on the
  contract, not the impl.
- **What we don't know.**
  - Default self-hostable impl: Keycloak (proven, heavy, Java) vs
    ZITADEL (Go, lighter, less mature) vs Authentik (Python, growing,
    SSO-focused) vs others.
  - Multi-source identity: city staff often live in city SSO (Azure AD,
    Okta); residents need their own. Does the Grid contract support
    multiple identity sources per Public Service, or one?
  - Civic attestation needs (ID.me-style) — out of scope for v1, or
    contract-level concern?
  - Adapter list for managed providers (Auth0, Clerk, Cognito) — which
    do we ship at v1?
- **When we need to resolve.** Phase 4 (Grid contracts) at the latest;
  ideally before Parking ships (Phase 8).

## 3. Multi-tenancy model

- **Problem.** One Parking deploy per city, or shared multi-tenant?
- **Why it matters.** Affects DB schema, auth scoping, every adapter,
  ops burden, and per-city cost. Hard to change later.
- **What we know.** Single-tenant per city is much simpler operationally
  and matches "easy to self-host." Multi-tenant is cheaper per-city
  *only when we're hosting many cities ourselves*.
- **What we don't know.**
  - At what scale does multi-tenancy become worth its complexity?
  - Can we ship single-tenant first and migrate later, or does that
    bake in assumptions we can't undo?
  - Does the Grid (e.g., audit, identity) have a multi-tenant story
    even if Public Services are single-tenant?
- **When we need to resolve.** Before the second city onboards to a
  PublicStack-managed Public Service. Single-tenant is the default
  assumption until we have a reason to revisit.

## 4. Flutter web accessibility

- **Problem.** Compliance suite requires WCAG 2.2 AA on Flutter web
  builds. Flutter web a11y has historically been weak (semantic tree
  gaps, screen reader bugs).
- **Why it matters.** Accessibility is a stated non-negotiable for
  PublicStack. If Flutter web can't pass a11y, the staff and kiosk
  apps can't ship as Flutter web — which forces a stack rethink.
- **What we know.** Flutter 3.41+ is the target. Apple/Google have been
  investing in Flutter web a11y; current state is better than 2023.
- **What we don't know.**
  - Does a current Flutter web build pass axe-core + manual screen
    reader testing on a non-trivial UI?
  - If gaps exist, are they fixable at the design-system level
    (`libraries/ui`) or are they framework limitations?
  - Is there a fallback (e.g., resident-facing app stays Flutter for
    mobile parity, but staff dashboard becomes plain web) that's
    cheaper than fighting Flutter?
- **When we need to resolve.** Phase 5 (compliance suite). Build a real
  a11y test against a non-trivial Flutter web build before locking the
  stack.

## 5. Public records / FOIA exports

- **Problem.** Every state's public-records law differs. Data export is
  a stated PublicStack non-negotiable.
- **Why it matters.** A Public Service that can't honor a valid records
  request is a legal liability for the city running it. Get the field
  taxonomy wrong and we're either over-disclosing (privacy violation)
  or under-disclosing (open-records violation).
- **What we know.** Every entity in `libraries/core/models/` must have
  a working export endpoint. Compliance suite checks that.
- **What we don't know.**
  - Which fields are mandatory disclosure vs exempt — varies by state,
    by data type, by requester.
  - Who decides per deployment (the city's records officer? a config
    flag set by the operator?).
  - PII redaction rules — automated or manual review?
  - Format requirements — CSV / JSON / PDF / structured per request?
- **When we need to resolve.** Before Parking ships in any real city
  (Phase 8). Until then, generic "every entity has an export endpoint"
  is enough.

## 6. Audit log immutability

- **Problem.** Audit is a Grid service. Real tamper-evidence needs more
  than append-only Postgres.
- **Why it matters.** A city subpoenaed for audit logs needs records
  that survive a "you tampered with these" challenge. Postgres
  append-only is convention, not cryptographic guarantee.
- **What we know.** Audit is in `grid/audit/`, with a Postgres-backed
  default adapter. Every write is ordered + timestamped.
- **What we don't know.**
  - Is hash-chained audit (each row's hash includes the previous row's
    hash) enough, or do we need external anchoring (e.g., periodic
    Merkle root publication to a public ledger)?
  - What's the performance cost of hash chains on hot write paths?
  - Adapter for managed audit (e.g., AWS QLDB, immutable S3 with
    object-lock) — ship at v1 or defer?
- **When we need to resolve.** Phase 4 (Grid contracts) — the contract
  shape needs to admit hash-chained / externally-anchored impls, even
  if the default adapter is plain Postgres.

## 7. Hosting cost floor

- **Problem.** "Cheap hosting" is a stated goal but we don't have a
  number for it.
- **Why it matters.** The single-VPS docker-compose path's whole
  purpose is to be the cheapest option. If a small-city Parking deploy
  needs $200/mo of VPS, the story falls apart. We need to know the
  actual floor.
- **What we know.** Target is "$10–20/mo VPS for a small-city Parking
  deploy" (PLAN.md §3). Postgres + Redis + Python services + Flutter
  web + nginx all on one box.
- **What we don't know.**
  - Real RAM/CPU footprint of the full stack idle and under realistic
    citation-volume load.
  - Smallest VPS tier (Hetzner CX21? DO basic? Vultr?) that holds up.
  - At what city size does single-VPS stop working?
- **When we need to resolve.** Phase 6 (hosting paths). Benchmark
  before claiming the floor in `deploy/HOSTING.md`.

---

This list grows. Add an entry whenever a hard problem surfaces that
isn't ready to be designed yet.
