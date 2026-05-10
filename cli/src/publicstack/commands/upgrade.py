"""`publicstack upgrade --to <version>` — stub for Phase 3."""

from __future__ import annotations

import typer

from publicstack import errors


def upgrade_cmd(
    to: str = typer.Option(..., "--to", help="Target blueprint version (e.g. 0.2.0)."),
) -> None:
    """Migrate a Public Service to a newer blueprint version (stub)."""
    errors.die(
        "upgrade is not yet implemented",
        "see blueprint/docs/migration-guides/ once a v0.2.0 release lands",
    )
