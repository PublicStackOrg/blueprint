# `publicstack-contracts`

Validates and diffs PublicStack contracts. Two formats: OpenAPI 3.1
(HTTP-shaped contracts) and JSON Schema Draft 2020-12 (everything
else). Format detection is by content; see
`../README.md` for the spec.

## Install

```bash
pipx install ./blueprint/contracts/tooling
pipx install --force ./blueprint/contracts/tooling   # update
```

The workspace `install.sh` installs this automatically when `pipx` is
on PATH.

## Commands

```bash
publicstack-contracts validate <path>     # exit 0 valid, 1 invalid, 2 unparseable
publicstack-contracts diff <old> <new>    # exit 0 no breaking, 1 breaking, 2 tool error
publicstack-contracts version
```

## OpenAPI semantic diff (optional)

For full OpenAPI breaking-change coverage, install
[`oasdiff`](https://github.com/oasdiff/oasdiff) separately:

```bash
brew install oasdiff
```

When `oasdiff` is on PATH, `publicstack-contracts diff` uses it. When
it's missing, the tool falls back to a pure-Python checker that covers
the same rule set (`JS001`–`JS008`) at lower fidelity. The fallback
keeps pipx-only installs functional.

## Develop

```bash
cd blueprint/contracts/tooling
poetry install --with dev
poetry run pytest
poetry run ruff check src tests
```
