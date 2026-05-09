# Security policy

`blueprint` is the template + spec every PublicStack Public Service is
generated from. A vulnerability in `blueprint` propagates to every
generated Public Service the next time they upgrade, so we take
disclosure seriously.

## Reporting a vulnerability

Email **`hello@publicstack.org`** with:

- A description of the issue and the impact you believe it has.
- Steps to reproduce, or a proof-of-concept if you have one.
- Affected `blueprint` version (see the repo's `VERSION` file) or, for
  issues in a generated Public Service, that Public Service's
  `BLUEPRINT_VERSION`.
- How you'd like to be credited (or not credited) in the disclosure.

**Please do not open a public GitHub issue for security reports.** A
public issue starts the clock on disclosure before we've had a chance
to fix the vulnerability.

We aim to acknowledge reports within **one week**. Triage,
remediation, and coordinated disclosure timelines depend on the
severity of the issue — we'll keep you informed throughout.

## Scope

In scope:

- The `blueprint` repo itself: template tree, compliance suite, CLI,
  Contract specs, Grid contracts, deployment recipes.
- Vulnerabilities a generated Public Service inherits from `blueprint`
  defaults (e.g., a misconfigured CSP in the template).

Out of scope (report to the relevant maintainer instead):

- Vulnerabilities in a specific Public Service's own code that aren't
  inherited from `blueprint`.
- Issues in third-party dependencies — please report those upstream
  first; we'll bump the pin once a fix is available.

## PGP

`blueprint` does not yet publish a PGP key. If you need to send
encrypted reports, contact us at `hello@publicstack.org` and we'll
arrange a key exchange. We expect to publish a stable PGP key once the
project has a regular maintenance cadence.

## Hall of fame

Researchers who report valid vulnerabilities will be credited in the
release notes for the fix (unless they prefer otherwise). PublicStack
does not run a paid bug-bounty program at this stage.
