from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from publicstack.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps"


@pytest.fixture()
def ps_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "ps"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)
    return root


def test_lint_missing_binary_warns(
    runner: CliRunner, ps_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "publicstack.commands.lint.shutil.which", lambda _name: None
    )
    result = runner.invoke(app, ["lint"])
    assert result.exit_code != 0
    assert "publicstack-compliance" in result.stderr


def test_lint_outside_ps_dies(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "publicstack.commands.lint.shutil.which",
        lambda _name: "/usr/bin/publicstack-compliance",
    )
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["lint"])
    assert result.exit_code != 0
    assert "BLUEPRINT_VERSION" in result.stderr


def test_lint_passes_through_args(
    runner: CliRunner, ps_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict = {}

    def fake_run(args, cwd, check):
        seen["args"] = list(args)
        seen["cwd"] = cwd
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(
        "publicstack.commands.lint.shutil.which",
        lambda _name: "/usr/bin/publicstack-compliance",
    )
    monkeypatch.setattr(
        "publicstack.commands.lint.subprocess.run", fake_run
    )

    result = runner.invoke(
        app, ["lint", "--check", "security", "--strict"]
    )
    assert result.exit_code == 0, result.stderr
    assert seen["args"][0] == "/usr/bin/publicstack-compliance"
    assert "run" in seen["args"]
    assert "--check" in seen["args"]
    assert "security" in seen["args"]
    assert "--strict" in seen["args"]
    assert seen["cwd"] == ps_root


def test_lint_forwards_exit_code(
    runner: CliRunner, ps_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(args, cwd, check):
        return subprocess.CompletedProcess(args, returncode=1)

    monkeypatch.setattr(
        "publicstack.commands.lint.shutil.which",
        lambda _name: "/usr/bin/publicstack-compliance",
    )
    monkeypatch.setattr(
        "publicstack.commands.lint.subprocess.run", fake_run
    )

    result = runner.invoke(app, ["lint"])
    assert result.exit_code == 1
