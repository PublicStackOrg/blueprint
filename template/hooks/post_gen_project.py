"""Cookiecutter post-generation hook.

Runs after the template is rendered into the output directory. Keeps
the steps that absolutely have to happen before the user touches the
generated tree, and nothing else.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path) -> None:
    """Run a command and surface failures clearly."""
    result = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"post-gen hook: `{' '.join(cmd)}` failed\n")
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)


def main() -> None:
    project_root = Path.cwd()

    # Stamp BLUEPRINT_VERSION (cookiecutter already substituted the value;
    # this is here in case the user wants a different post-gen ritual).

    # Initialise a git repo so the generated tree is immediately committable.
    if not (project_root / ".git").exists():
        run(["git", "init", "--initial-branch=main"], cwd=project_root)

    sys.stdout.write(
        "\n"
        "  generated. Next steps:\n"
        "    cd {{ cookiecutter.public_service_name }}\n"
        "    npm install && poetry install\n"
        "    ./scripts/dev.sh\n"
        "\n"
    )


if __name__ == "__main__":
    main()
