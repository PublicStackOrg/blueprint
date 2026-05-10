from __future__ import annotations

import json
import shutil
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


def test_add_app_generates_and_wires(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "app", "inspector"])
    assert result.exit_code == 0, result.stderr

    assert (ps_root / "apps" / "inspector" / "pubspec.yaml").is_file()
    assert (ps_root / "apps" / "inspector" / "lib" / "main.dart").is_file()

    pkg = json.loads((ps_root / "package.json").read_text())
    assert "flutter:inspector" in pkg["scripts"]


def test_add_app_kind_web_stub(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "app", "inspector", "--kind", "web"])
    assert result.exit_code != 0
    assert "not yet implemented" in result.stderr.lower()


def test_add_app_rejects_existing(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "app", "resident"])  # already in fixture
    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()
