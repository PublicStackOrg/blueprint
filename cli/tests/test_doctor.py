from __future__ import annotations

from typing import Any

import pytest
from typer.testing import CliRunner

from publicstack import shell
from publicstack.cli import app


@pytest.fixture()
def all_tools_present(monkeypatch: pytest.MonkeyPatch) -> None:
    versions = {
        "python3": "3.13.1",
        "node": "20.10.0",
        "npm": "10.2.0",
        "poetry": "1.8.3",
        "docker": "27.0.0",
        "gh": "2.45.0",
        "flutter": "3.41.0",
        "terraform": "1.7.0",
        "cookiecutter": "2.6.0",
    }

    def fake_tool_version(binary: str, *_args: str) -> str | None:
        return versions.get(binary)

    monkeypatch.setattr(shell, "tool_version", fake_tool_version)
    monkeypatch.setattr(shell, "gh_authenticated", lambda: True)


@pytest.fixture()
def required_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_tool_version(binary: str, *_args: Any) -> str | None:
        if binary == "docker":
            return None
        return "99.0.0"

    monkeypatch.setattr(shell, "tool_version", fake_tool_version)
    monkeypatch.setattr(shell, "gh_authenticated", lambda: True)


def test_doctor_passes_when_all_present(
    runner: CliRunner, all_tools_present: None
) -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.stderr
    assert "ok" in result.stdout
    assert "FAIL" not in result.stdout


def test_doctor_fails_when_required_missing(
    runner: CliRunner, required_missing: None
) -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code != 0
    assert "FAIL" in result.stdout


def test_doctor_flags_unauthenticated_gh(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(shell, "tool_version", lambda *_a, **_k: "99.0.0")
    monkeypatch.setattr(shell, "gh_authenticated", lambda: False)
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code != 0
    assert "not authenticated" in result.stdout
