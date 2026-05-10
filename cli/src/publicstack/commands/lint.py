"""`publicstack lint` — delegates to the publicstack-compliance CLI."""

from __future__ import annotations

import shutil
import subprocess

import typer

from publicstack import errors
from publicstack.paths import find_public_service_root


def lint_cmd(ctx: typer.Context) -> None:
    """Run the PublicStack compliance suite against the current Public Service.

    Thin subprocess wrapper around `publicstack-compliance run`. Extra
    arguments (e.g. `--check security --strict`) pass through.
    """
    binary = shutil.which("publicstack-compliance")
    if binary is None:
        errors.die(
            "publicstack-compliance CLI not on PATH",
            "install it: `pipx install <repo>/blueprint/compliance`",
        )
        return

    try:
        ps_root = find_public_service_root()
    except FileNotFoundError as e:
        errors.die(
            str(e),
            "cd into a generated Public Service (one with a BLUEPRINT_VERSION file)",
        )
        return

    args = [binary, "run", *ctx.args]
    result = subprocess.run(args, cwd=ps_root, check=False)
    raise typer.Exit(result.returncode)
