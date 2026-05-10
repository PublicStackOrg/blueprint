"""`publicstack doctor` — toolchain + auth health check."""

from __future__ import annotations

from dataclasses import dataclass

import typer
from packaging.version import InvalidVersion, Version

from publicstack import errors, shell


@dataclass(frozen=True)
class Check:
    name: str
    binary: str
    minimum: str | None
    required: bool
    extra: str = ""  # appended to the detail column


_CHECKS: tuple[Check, ...] = (
    Check("python", "python3", "3.13", required=True),
    Check("node", "node", "20.0", required=True),
    Check("npm", "npm", "10.0", required=True),
    Check("poetry", "poetry", None, required=True),
    Check("docker", "docker", None, required=True),
    Check("gh", "gh", None, required=True),
    Check("flutter", "flutter", "3.41", required=False),
    Check("terraform", "terraform", None, required=False),
    Check("cookiecutter", "cookiecutter", None, required=False),
)


def _ge(version: str | None, minimum: str | None) -> bool:
    if version is None:
        return False
    if minimum is None:
        return True
    try:
        return Version(version) >= Version(minimum)
    except InvalidVersion:
        return False


def doctor_cmd() -> None:
    """Verify required and optional tools are present and recent enough."""
    rows: list[tuple[str, str, str, str]] = []  # name, found, required, status
    any_required_missing = False

    for c in _CHECKS:
        version = shell.tool_version(c.binary)
        found = "—" if version is None else version
        required = c.minimum or "any"
        if c.required and not c.minimum:
            required = "any (required)"
        elif c.required:
            required = f">={c.minimum}"

        passed = _ge(version, c.minimum) if c.minimum else (version is not None)
        if c.name == "gh" and passed and not shell.gh_authenticated():
            passed = False
            found = (found or "?") + " (not authenticated)"

        if c.required and not passed:
            any_required_missing = True
            status = "FAIL"
        elif not passed:
            status = "warn"
        else:
            status = "ok"

        rows.append((c.name, found, required, status))

    name_w = max(len(r[0]) for r in rows)
    found_w = max(len(r[1]) for r in rows)
    req_w = max(len(r[2]) for r in rows)
    typer.echo(
        f"{'tool':<{name_w}}  {'found':<{found_w}}  {'required':<{req_w}}  status"
    )
    typer.echo("-" * (name_w + found_w + req_w + 14))
    for name, found, required, status in rows:
        typer.echo(
            f"{name:<{name_w}}  {found:<{found_w}}  {required:<{req_w}}  {status}"
        )

    if any_required_missing:
        errors.die(
            "one or more required tools are missing or out-of-date",
            "install the listed tools and re-run `publicstack doctor`",
        )
