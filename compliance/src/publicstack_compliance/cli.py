"""publicstack-compliance CLI entrypoint."""

from __future__ import annotations

from pathlib import Path

import typer

from publicstack_compliance import __version__, errors
from publicstack_compliance.checks import CHECKS, list_check_names
from publicstack_compliance.findings import (
    has_breaking,
    upgrade_warns_to_breaking,
)
from publicstack_compliance.ps_root import find_public_service_root
from publicstack_compliance.report import format_json, format_text
from publicstack_compliance.runner import run_checks

app = typer.Typer(
    name="publicstack-compliance",
    help="Verify a generated Public Service meets PublicStack standards.",
    no_args_is_help=True,
    add_completion=True,
)


@app.callback()
def _root() -> None:
    """Multi-command shell."""


@app.command("version")
def version_cmd() -> None:
    """Print the publicstack-compliance version."""
    typer.echo(f"publicstack-compliance {__version__}")


@app.command("list-checks")
def list_checks_cmd() -> None:
    """List the registered checks."""
    for name in list_check_names():
        typer.echo(name)


@app.command("run")
def run_cmd(
    check: list[str] = typer.Option(
        None,
        "--check",
        "-c",
        help="Run only the named check(s); repeat to add more. Default: all.",
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text | json."
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Treat warnings as breaking failures."
    ),
    path: Path = typer.Option(
        None,
        "--path",
        help="Path inside (or to) a Public Service. Defaults to CWD.",
    ),
) -> None:
    """Run the compliance suite against a Public Service.

    Exit codes: 0 all pass, 1 breaking findings, 2 tool error.
    """
    if output_format not in ("text", "json"):
        errors.die(f"unknown --format: {output_format}", "use 'text' or 'json'", code=2)

    try:
        ps_root = find_public_service_root(path)
    except FileNotFoundError as e:
        errors.die(str(e), "cd into a generated Public Service", code=2)
        return

    selected = check or None
    if selected:
        unknown = [c for c in selected if c not in CHECKS]
        if unknown:
            errors.die(
                f"unknown check(s): {', '.join(unknown)}",
                f"valid: {', '.join(list_check_names())}",
                code=2,
            )

    try:
        findings = run_checks(ps_root, selected)
    except KeyError as e:
        errors.die(str(e), code=2)
        return

    if strict:
        findings = upgrade_warns_to_breaking(findings)

    if output_format == "json":
        typer.echo(format_json(findings, ps_root))
    else:
        typer.echo(format_text(findings, ps_root))

    if has_breaking(findings):
        raise typer.Exit(1)
