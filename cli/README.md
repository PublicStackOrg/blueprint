# `publicstack` CLI

Command-line tool for the PublicStack ecosystem. Wraps cookiecutter to
scaffold new Public Services from `blueprint/template/`, plus convenience
commands for adding internal services, Flutter apps, and contracts inside
an existing Public Service.

## Install

```bash
pipx install ./blueprint/cli              # from a workspace clone
pipx install --force ./blueprint/cli      # update an existing install
```

The workspace `install.sh` does this automatically on machines that have
`pipx` on PATH.

## Commands

```
publicstack new service <name> [--push] [--output-dir <dir>] [--slug <s>]
publicstack add api <name>
publicstack add app <name> [--kind flutter]
publicstack add contract <name> --version v1 [--exposes|--consumes]
publicstack doctor
publicstack version
publicstack upgrade --to <v>      # stub; lands in a future phase
publicstack lint                  # stub; ships with the compliance suite
```

`publicstack new service` writes locally by default. Pass `--push` to also
create `PublicStackOrg/<slug>` on GitHub and push the initial commit.

## Develop

```bash
cd blueprint/cli
poetry install --with dev
poetry run pytest
poetry run ruff check src tests

# Re-bundle the blueprint template after editing ../template/:
python tools/sync_blueprint_template.py
```

The CLI bundles `blueprint/template/` and per-add cookiecutters inside its
wheel. `tools/sync_blueprint_template.py --check` runs in CI to ensure the
bundled copy matches the source-of-truth tree.

## Layout

```
src/publicstack/
├── cli.py                          # Typer root
├── commands/                       # one module per command
├── codegen/                        # cookiecutter wrapper + slug rules
├── editors/                        # idempotent in-place edits to wiring files
└── templates/
    ├── _blueprint/                 # synced from ../template/
    ├── service/                    # cookiecutter for `add api`
    ├── app/                        # cookiecutter for `add app`
    └── contract/                   # cookiecutter for `add contract`
```
