# `compliance/`

The PublicStack compliance suite — a Python package that runs against
any generated Public Service and verifies it meets PublicStack
standards.

**Status:** empty placeholder. Filled in during **Phase 5** of
[`../docs/PLAN.md`](../docs/PLAN.md).

What lands here:

- `pyproject.toml` — Poetry-managed package, installable via
  `pipx install publicstack-compliance` or `poetry add` from a
  generated Public Service.
- `src/publicstack_compliance/checks/` — one module per check
  category: `grid_integration`, `contract_compat`, `accessibility`,
  `data_export`, `security`, `observability`.
- `src/publicstack_compliance/cli.py` — entrypoint for
  `publicstack-compliance run`.
- `tests/` — tests for the suite itself.

The suite runs in CI (`publicstack-compliance run --pr`) and is also
runnable standalone, so an outside org forking a Public Service can
verify it stays compliant.
