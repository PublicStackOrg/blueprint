"""`publicstack version`."""

from __future__ import annotations

import typer

from publicstack import __version__
from publicstack.paths import bundled_blueprint_version


def version_cmd() -> None:
    """Print CLI and bundled blueprint versions."""
    typer.echo(f"publicstack {__version__}")
    typer.echo(f"blueprint   {bundled_blueprint_version()}")
