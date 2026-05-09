# `cli/`

The `publicstack` command-line tool — a Python package, installable via
`pipx install ./cli` (or eventually from PyPI).

**Status:** empty placeholder. Filled in during **Phase 3** of
[`../docs/PLAN.md`](../docs/PLAN.md).

Planned commands (see `docs/PLAN.md` §5 for the full list):

```
publicstack new service <name>          # generate a new Public Service
publicstack add api|app|contract|grid   # add an internal piece
publicstack lint                        # run the compliance suite locally
publicstack doctor                      # toolchain + env health check
publicstack upgrade --to <version>      # migrate to a newer blueprint version
publicstack version                     # report blueprint + CLI version
```

`publicstack new service` wraps `cookiecutter` against `../template/`
and handles the surrounding ergonomics: GitHub repo creation under
`PublicStackOrg`, AGPL header insertion, post-generation sanity checks.
