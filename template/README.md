# `template/`

The cookiecutter scaffold for a new PublicStack Public Service. Running
`cookiecutter` (or eventually `publicstack new service`) against this
directory materialises a working monorepo for one Public Service.

## Layout

```
template/
├── cookiecutter.json                              # variables + defaults
├── hooks/
│   └── post_gen_project.py                        # git init, post-gen messaging
└── {{cookiecutter.public_service_name}}/          # the scaffold tree
    ├── README.md
    ├── LICENSE                                    # AGPL-3.0
    ├── LICENSING.md
    ├── CLAUDE.md                                  # per-PS Claude context
    ├── BLUEPRINT_VERSION
    ├── .env.example
    ├── package.json                               # NX workspace
    ├── nx.json
    ├── pyproject.toml                             # Poetry root, path deps
    ├── apps/                                      # Flutter apps
    ├── services/                                  # Python services
    ├── libraries/                                 # shared Python + Dart
    ├── contracts/                                 # Phase 4
    ├── grid/                                      # Phase 4
    ├── exports/                                   # Phase 5
    ├── deploy/                                    # Phase 6
    ├── docs/, tests/, scripts/, tools/, seeds/, secrets/
    └── .github/workflows/
```

## Variables (see `cookiecutter.json`)

| Variable | Default | Used in |
|---|---|---|
| `public_service_name` | `ExamplePS` | titles, repo dir name |
| `public_service_slug` | derived | package names, db, container names |
| `python_package` | derived | Poetry package name |
| `description` | generic one-liner | README + pyproject.toml |
| `github_org` | `PublicStackOrg` | CI metadata |
| `blueprint_version` | current `VERSION` | stamped into BLUEPRINT_VERSION |

## Use

```bash
# Until the publicstack CLI ships (Phase 3), drive cookiecutter directly:
cookiecutter blueprint/template/ \
    --no-input \
    public_service_name=Parking \
    description="Open-source parking citations and meter management."

# Output: ./Parking/, ready to:
cd Parking && npm install && poetry install && ./scripts/dev.sh
```

The post-gen hook initialises a git repo. Push it to
`PublicStackOrg/<name>` and the standard CI workflow ships with it.
