"""Thin wrapper around cookiecutter so commands don't import it directly."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter


def run(
    template_dir: Path,
    *,
    output_dir: Path,
    extra_context: dict[str, Any],
    overwrite_if_exists: bool = False,
) -> Path:
    """Render `template_dir` into `output_dir`. Returns the generated path."""
    out = cookiecutter(
        str(template_dir),
        no_input=True,
        output_dir=str(output_dir),
        extra_context=extra_context,
        overwrite_if_exists=overwrite_if_exists,
    )
    return Path(out)
