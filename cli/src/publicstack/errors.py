"""ANSI-coded stderr output. No external deps."""

from __future__ import annotations

import os
import sys

import typer

_RED = "\033[1;31m"
_YELLOW = "\033[1;33m"
_BLUE = "\033[1;34m"
_GREEN = "\033[1;32m"
_RESET = "\033[0m"


def _colorize() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stderr.isatty()


def _emit(prefix: str, color: str, message: str, suggestion: str | None) -> None:
    c = _colorize()
    p = f"{color}{prefix}{_RESET}" if c else prefix
    sys.stderr.write(f"{p} {message}\n")
    if suggestion:
        sys.stderr.write(f"  {suggestion}\n")


def info(message: str) -> None:
    _emit("info:", _BLUE, message, None)


def ok(message: str) -> None:
    _emit("ok:", _GREEN, message, None)


def warn(message: str, suggestion: str | None = None) -> None:
    _emit("warn:", _YELLOW, message, suggestion)


def error(message: str, suggestion: str | None = None) -> None:
    _emit("error:", _RED, message, suggestion)


def die(message: str, suggestion: str | None = None, code: int = 1) -> None:
    error(message, suggestion)
    raise typer.Exit(code)
