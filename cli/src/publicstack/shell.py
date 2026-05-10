"""Shell + version-string helpers for `doctor` and the GitHub flow."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolStatus:
    name: str
    found: bool
    version: str | None
    required: str | None  # minimum version, e.g. ">=3.13"
    ok: bool
    detail: str = ""


def which(name: str) -> str | None:
    return shutil.which(name)


def run(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, capture_output=True, text=True)


_VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


def _first_version(text: str) -> str | None:
    m = _VERSION_RE.search(text)
    return m.group(1) if m else None


def _parse_python(text: str) -> str | None:
    return _first_version(text)


def _parse_node(text: str) -> str | None:
    return _first_version(text.lstrip("v"))


def _parse_npm(text: str) -> str | None:
    return _first_version(text)


def _parse_poetry(text: str) -> str | None:
    return _first_version(text)


def _parse_docker(text: str) -> str | None:
    return _first_version(text)


def _parse_gh(text: str) -> str | None:
    # `gh version 2.x.y (date)\nhttps://...`
    return _first_version(text)


def _parse_flutter(text: str) -> str | None:
    # First line: "Flutter 3.x.y • channel stable • https://..."
    return _first_version(text.splitlines()[0] if text else "")


def _parse_terraform(text: str) -> str | None:
    return _first_version(text)


def _parse_cookiecutter(text: str) -> str | None:
    return _first_version(text)


_PARSERS = {
    "python": _parse_python,
    "python3": _parse_python,
    "node": _parse_node,
    "npm": _parse_npm,
    "poetry": _parse_poetry,
    "docker": _parse_docker,
    "gh": _parse_gh,
    "flutter": _parse_flutter,
    "terraform": _parse_terraform,
    "cookiecutter": _parse_cookiecutter,
}


def tool_version(binary: str, *args: str) -> str | None:
    """Run `<binary> --version` (or override args) and parse out a version."""
    if which(binary) is None:
        return None
    cmd = [binary, *args] if args else [binary, "--version"]
    try:
        result = run(cmd)
    except FileNotFoundError:
        return None
    output = (result.stdout or "") + (result.stderr or "")
    parser = _PARSERS.get(binary, _first_version)
    return parser(output)


def gh_authenticated() -> bool:
    if which("gh") is None:
        return False
    result = run(["gh", "auth", "status"])
    return result.returncode == 0
