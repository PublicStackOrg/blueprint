"""publicstack-contracts CLI entrypoint."""

from __future__ import annotations

from pathlib import Path

import typer

from publicstack_contracts import __version__, errors
from publicstack_contracts.detect import AmbiguousFormatError, detect
from publicstack_contracts.diff import diff_jsonschema, diff_openapi
from publicstack_contracts.diff.report import has_breaking
from publicstack_contracts.load import LoadError, load
from publicstack_contracts.validate import validate_jsonschema, validate_openapi

app = typer.Typer(
    name="publicstack-contracts",
    help="Validate and diff PublicStack contracts (OpenAPI 3.1 + JSON Schema).",
    no_args_is_help=True,
    add_completion=True,
)


@app.callback()
def _root() -> None:
    """Multi-command shell. Forces Typer to keep the multi-command tree even
    when only one subcommand is registered."""


@app.command("version")
def version_cmd() -> None:
    """Print the publicstack-contracts version."""
    typer.echo(f"publicstack-contracts {__version__}")


@app.command("validate")
def validate_cmd(
    path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, readable=True
    ),
) -> None:
    """Check that a contract file is well-formed against its detected format.

    Exit codes: 0 valid, 1 invalid, 2 unparseable.
    """
    try:
        doc = load(path)
    except LoadError as e:
        errors.die(str(e), code=2)
        return

    try:
        fmt = detect(doc)
    except AmbiguousFormatError as e:
        errors.die(str(e), code=2)
        return

    findings = validate_openapi(doc) if fmt == "openapi" else validate_jsonschema(doc)
    if findings:
        errors.error(f"{path} is invalid as {fmt}:")
        for f in findings:
            typer.echo(f"  - {f.path}: {f.message}")
        raise typer.Exit(1)

    errors.ok(f"{path} valid ({fmt})")


@app.command("diff")
def diff_cmd(
    old: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
    new: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
) -> None:
    """Detect back-compat-breaking changes between two contract versions.

    Exit codes: 0 no breaking, 1 breaking found, 2 tool error.
    """
    try:
        old_doc = load(old)
        new_doc = load(new)
    except LoadError as e:
        errors.die(str(e), code=2)
        return

    try:
        old_fmt = detect(old_doc)
        new_fmt = detect(new_doc)
    except AmbiguousFormatError as e:
        errors.die(str(e), code=2)
        return

    if old_fmt != new_fmt:
        errors.die(
            f"format mismatch: {old} is {old_fmt}, {new} is {new_fmt}",
            "both files must use the same contract format",
            code=2,
        )
        return

    if old_fmt == "openapi":
        findings = diff_openapi(old_doc, new_doc, old_path=old, new_path=new)
    else:
        findings = diff_jsonschema(old_doc, new_doc)

    if findings:
        for f in findings:
            tag = "BREAK" if f.is_breaking() else "info "
            typer.echo(f"  [{tag}] {f.rule} {f.path}: {f.message}")

    if has_breaking(findings):
        errors.error(f"{old} → {new}: breaking changes detected")
        raise typer.Exit(1)

    errors.ok(f"{old} → {new}: no breaking changes")
