# `template/`

Cookiecutter scaffold tree. When the `publicstack` CLI runs
`publicstack new service <name>`, it materializes everything under
`template/{{cookiecutter.public_service_name}}/` into a new Public
Service repo.

**Status:** empty placeholder. Filled in during **Phase 2** of
[`../docs/PLAN.md`](../docs/PLAN.md).

What lands here:

- `cookiecutter.json` — the variables the user fills in at generation
  time.
- `hooks/` — post-generation hooks (rename, init git, etc.).
- `{{cookiecutter.public_service_name}}/` — the actual scaffold tree.
  See `docs/PLAN.md` §1 for the full layout.
