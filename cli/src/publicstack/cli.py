"""publicstack CLI entrypoint."""

from __future__ import annotations

import typer

from publicstack.commands.add import add_app
from publicstack.commands.doctor import doctor_cmd
from publicstack.commands.lint import lint_cmd
from publicstack.commands.new import new_app
from publicstack.commands.upgrade import upgrade_cmd
from publicstack.commands.version_cmd import version_cmd

app = typer.Typer(
    name="publicstack",
    help="PublicStack CLI — scaffold and maintain Public Services.",
    no_args_is_help=True,
    add_completion=True,
)

app.add_typer(new_app, name="new")
app.add_typer(add_app, name="add")


@app.command("doctor")
def _doctor() -> None:
    """Check toolchain and authentication health."""
    doctor_cmd()


@app.command("version")
def _version() -> None:
    """Print CLI and bundled blueprint versions."""
    version_cmd()


app.command("upgrade")(upgrade_cmd)
app.command("lint")(lint_cmd)
