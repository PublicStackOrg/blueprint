from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import tomlkit
from ruamel.yaml import YAML
from typer.testing import CliRunner

from publicstack.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps"


@pytest.fixture()
def ps_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "ps"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)
    return root


def test_add_api_generates_and_wires(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "api", "scrubber"])
    assert result.exit_code == 0, result.stderr

    assert (ps_root / "services" / "scrubber" / "pyproject.toml").is_file()
    assert (ps_root / "services" / "scrubber" / "Dockerfile").is_file()

    compose = YAML().load((ps_root / "docker-compose.yml").read_text())
    assert "scrubber" in compose["services"]

    pyproject = tomlkit.parse((ps_root / "pyproject.toml").read_text())
    assert "scrubber" in pyproject["tool"]["poetry"]["dependencies"]


def test_add_api_rejects_reserved(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "api", "redis"])
    assert result.exit_code != 0
    assert "reserved" in result.stderr.lower()


def test_add_api_rejects_existing(ps_root: Path, runner: CliRunner) -> None:
    (ps_root / "services" / "scrubber").mkdir()
    result = runner.invoke(app, ["add", "api", "scrubber"])
    assert result.exit_code != 0
    assert "already exists" in result.stderr.lower()


def test_add_api_outside_ps(tmp_path: Path, runner: CliRunner,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["add", "api", "scrubber"])
    assert result.exit_code != 0
    assert "BLUEPRINT_VERSION" in result.stderr
