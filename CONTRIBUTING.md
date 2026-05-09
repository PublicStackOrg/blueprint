# Contributing to `blueprint`

`blueprint` defines the shape of every PublicStack Public Service. A
change here propagates to every Public Service the next time it
upgrades, so the bar for changes is high. This doc covers what we
expect from contributions and how to get one through review.

## Before opening a PR

1. **Read [`docs/PLAN.md`](./docs/PLAN.md).** It's the source of truth
   for what `blueprint` is and where it's going. If your change isn't
   anchored to a phase in the plan, open an issue first to discuss.
2. **Check [`docs/SPIKES.md`](./docs/SPIKES.md).** If your change
   touches an unresolved spike (identity, payments execution,
   multi-tenancy, FOIA, audit immutability, hosting cost), say so in
   the PR — those areas need extra care.
3. **Skim the [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).** Project
   spaces are governed by Contributor Covenant 2.1.

## Small changes — typos, doc fixes, obvious bugs

Open a PR directly. Reference the file/section you're fixing in the
title. No issue or RFC needed.

## Substantive changes — go through the RFC process

Anything that changes the shape of a generated Public Service goes
through an RFC. That includes:

- New top-level directories or files in the `template/` tree.
- New or changed Contracts (Contract format spec, exposed Contracts).
- New or changed Grid contracts.
- New compliance checks, or changes to how existing checks work.
- New CLI commands or breaking changes to existing ones.
- Changes that bump the `blueprint` major or minor version.

The RFC process:

1. Open a draft PR adding a new file under `docs/RFCs/` named
   `NNNN-short-slug.md` (next free number).
2. The RFC describes: motivation, proposed change, alternatives
   considered, migration story for existing Public Services, and the
   open questions you'd like reviewers to weigh in on.
3. Tag at least one core maintainer for review. Discussion happens in
   the PR thread.
4. Once accepted, the RFC merges first, then the implementation PR
   references it.

For *trivially small* changes inside one of the categories above
(renaming a CLI flag, fixing a Grid contract typo) — judgment call,
err toward an RFC. The cost is low and the precedent matters.

## Code style

Per-language conventions land alongside the code in their respective
phases. For now, follow the existing patterns in
`/Users/leonidbelyi/personal/palateful/` (the reference project the
template is modeled on) and the conventions in [`CLAUDE.md`](./CLAUDE.md).

Cross-cutting expectations:

- **Default to no comments.** Code should explain *what*; comments
  explain *why* — and only when *why* is non-obvious.
- **Don't add abstractions for hypothetical callers.** Three real
  callers, then a helper.
- **Don't introduce backwards-compat shims for unreleased features.**
  Until 1.0, breaking changes are allowed; document them in
  `docs/migration-guides/`.

## License

Contributions are accepted under the inbound=outbound principle: by
opening a PR you agree your contribution is licensed under
[AGPL-3.0](./LICENSE), the same as the rest of the project. There is
no CLA. See [`LICENSING.md`](./LICENSING.md) for the rationale.

## Questions

Email `hello@publicstack.org` or open a discussion in the
`PublicStackOrg/blueprint` GitHub repo.
