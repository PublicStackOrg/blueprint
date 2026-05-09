# Governance

This document is the placeholder for PublicStack's formal governance
model. It will grow into something real as the project does. Today,
the project is small enough that the answer to most governance
questions is "ask the maintainer."

## Today

- **Stewarding entity:** none yet. The project is currently maintained
  by Leonid Belyi (`hello@publicstack.org`). Decisions about
  `blueprint` are made by the maintainer in consultation with anyone
  contributing at the time.
- **Decision-making:** by maintainer review on every PR. RFCs (see
  [`CONTRIBUTING.md`](./CONTRIBUTING.md)) are the formal channel for
  substantive proposals.
- **Conflict resolution:** `hello@publicstack.org`, then escalation
  path is "fork the repo and prove the alternative works."

## What changes when

We expect to formalize this document along the following triggers:

- **Second active contributor.** Define what "core maintainer" means
  and how someone becomes one. Add a `MAINTAINERS.md` listing the
  current set.
- **First production deployment by a third party.** Add a public
  roadmap process and an issue-triage cadence.
- **Stewarding entity stood up.** Likely a non-profit or a fiscal
  host; document its relationship to the codebase, the trademark, and
  the managed-hosting offering.
- **Project gets large enough that the maintainer can't review every
  PR personally.** Move to a per-area code-owner model
  (`CODEOWNERS`); document the path from contributor to maintainer.

If you want to push any of those triggers earlier, open an issue.

## What governance does NOT cover

- **Per-Public-Service governance.** Each Public Service generated
  from `blueprint` is its own repo and its own community. They inherit
  PublicStack's defaults (AGPL-3.0, Contributor Covenant) but set
  their own maintainership.
- **Hosted-tier service decisions.** PublicStack's managed-hosting
  offering is operationally separate from the open-source project.
  Pricing, SLAs, customer-support policy — none of those are
  governance concerns for this repo.

## Contact

`hello@publicstack.org` for governance questions.
