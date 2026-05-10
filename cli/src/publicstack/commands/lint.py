"""`publicstack lint` — stub. Real impl ships with the compliance suite."""

from __future__ import annotations

from publicstack import errors


def lint_cmd() -> None:
    """Run the PublicStack compliance suite locally (stub)."""
    errors.die(
        "lint is not yet implemented",
        "the compliance suite ships in Phase 5 (blueprint/compliance/)",
    )
