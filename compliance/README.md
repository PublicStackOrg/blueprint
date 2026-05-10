# `publicstack-compliance`

Compliance suite for PublicStack Public Services. Runs against a generated
PS and verifies six standards: data_export, contract_compat,
grid_integration, security, observability, accessibility.

## Install

```bash
pipx install ./blueprint/compliance
pipx install --force ./blueprint/compliance       # update
```

The workspace `install.sh` does this automatically when `pipx` is on PATH.

For the accessibility check, also install Chromium for Playwright once:

```bash
playwright install chromium
```

`gitleaks` (used by the security check) is optional — install via your
package manager (`brew install gitleaks`, `apt-get install gitleaks`).
The check skips with a warning if missing.

## Commands

```bash
publicstack-compliance run                       # run all checks against CWD
publicstack-compliance run --check data_export   # one check
publicstack-compliance run --format json         # machine-readable
publicstack-compliance run --strict              # treat warns as breaking
publicstack-compliance list-checks
publicstack-compliance version
```

Exit codes: `0` all pass, `1` breaking findings, `2` tool error.

`publicstack lint` (in the main publicstack CLI) is a thin subprocess
wrapper around `publicstack-compliance run` — flags pass through.

## Develop

```bash
cd blueprint/compliance
poetry install --with dev
poetry run pytest
poetry run ruff check src tests
```

The `publicstack-contracts` library is consumed via a path-dep against the
sibling `blueprint/contracts/tooling/` directory; outside-org installs pull
the same package from PyPI once we publish it.

## Vendored axe-core

`src/publicstack_compliance/_vendor/axe.min.js` is axe-core (MPL-2.0). The
license header is intact in the file. Update via:

```bash
curl -L https://unpkg.com/axe-core/axe.min.js \
  -o src/publicstack_compliance/_vendor/axe.min.js
```
