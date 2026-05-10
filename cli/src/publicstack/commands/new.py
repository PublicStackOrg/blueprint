"""`publicstack new service <name>`."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer

from publicstack import errors, shell
from publicstack.codegen import slug as slug_mod
from publicstack.codegen.cookiecutter_runner import run as cookiecutter_run
from publicstack.paths import blueprint_template_dir, bundled_blueprint_version

new_app = typer.Typer(help="Scaffold new things from blueprint.", no_args_is_help=True)

_GH_ORG = "PublicStackOrg"


@new_app.command("service")
def service_cmd(
    name: str = typer.Argument(..., help="Public Service name (display or slug)."),
    output_dir: Path = typer.Option(
        Path.cwd(),
        "--output-dir",
        "-o",
        help="Directory to generate the new Public Service into.",
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Override the derived slug (lowercase, kebab/snake-case)."
    ),
    push: bool = typer.Option(
        False,
        "--push",
        help=f"Create {_GH_ORG}/<slug> on GitHub and push the initial commit.",
    ),
    description: str = typer.Option(
        "An open-source PublicStack Public Service.",
        "--description",
        help="One-line description (used in README and gh repo create).",
    ),
) -> None:
    """Generate a new Public Service from blueprint."""
    derived = slug or slug_mod.derive_slug(name)
    if not slug_mod.is_valid_slug(derived):
        errors.die(
            f"derived slug '{derived}' is not valid",
            "pass --slug with [a-z][a-z0-9_-]{1,49}",
        )

    output_dir = output_dir.resolve()
    if not output_dir.exists():
        errors.die(
            f"output directory does not exist: {output_dir}",
            "create it first or pass --output-dir",
        )
    target = output_dir / derived
    if target.exists():
        errors.die(
            f"target already exists: {target}",
            "remove it or pick a different name",
        )

    if shell.which("git") is None:
        errors.die("git is not on PATH", "install git and re-run")

    if push:
        if shell.which("gh") is None:
            errors.die("--push requires gh on PATH", "install gh and re-run")
        if not shell.gh_authenticated():
            errors.die(
                "gh is not authenticated",
                "run `gh auth login` and re-run with --push",
            )
        existing = shell.run(["gh", "repo", "view", f"{_GH_ORG}/{derived}"])
        if existing.returncode == 0:
            errors.die(
                f"{_GH_ORG}/{derived} already exists on GitHub",
                "pick a different slug or drop --push",
            )

    extra = {
        "public_service_name": name,
        "public_service_slug": derived,
        "python_package": slug_mod.derive_python_package(derived),
        "description": description,
        "github_org": _GH_ORG,
        "blueprint_version": bundled_blueprint_version(),
    }

    with blueprint_template_dir() as template_dir:
        generated = cookiecutter_run(
            template_dir, output_dir=output_dir, extra_context=extra
        )

    errors.ok(f"generated {generated}")

    if push:
        _push_to_github(generated, derived, description)


def _push_to_github(repo: Path, slug: str, description: str) -> None:
    """Create the GitHub repo and push the initial commit. Best-effort: failures
    surface to stderr but the local tree is preserved either way."""
    full = f"{_GH_ORG}/{slug}"

    create = subprocess.run(
        [
            "gh",
            "repo",
            "create",
            full,
            "--public",
            "--license",
            "AGPL-3.0",
            "--description",
            description,
        ],
        capture_output=True,
        text=True,
    )
    if create.returncode != 0:
        errors.warn(
            f"gh repo create failed: {create.stderr.strip()}",
            "create the repo manually and push when ready",
        )
        return

    cmds = [
        ["git", "remote", "add", "origin", f"git@github.com:{full}.git"],
        ["git", "add", "-A"],
        [
            "git",
            "commit",
            "-m",
            f"Initial commit (blueprint v{bundled_blueprint_version()})",
        ],
        ["git", "branch", "-M", "main"],
        ["git", "push", "-u", "origin", "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
        if result.returncode != 0:
            errors.warn(
                f"`{' '.join(cmd)}` failed: {result.stderr.strip()}",
                "finish the push manually",
            )
            return

    errors.ok(f"pushed to https://github.com/{full}")
