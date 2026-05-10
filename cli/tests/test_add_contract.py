from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from publicstack.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps"


@pytest.fixture()
def ps_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "ps"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)
    return root


def test_add_contract_exposes(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(
        app, ["add", "contract", "citations", "--version", "v1", "--exposes"]
    )
    assert result.exit_code == 0, result.stderr
    target = ps_root / "contracts" / "exposed" / "citations.v1.yaml"
    assert target.is_file()
    parsed = yaml.safe_load(target.read_text())
    assert parsed["info"]["title"] == "citations"
    assert parsed["info"]["version"] == "v1"


def test_add_contract_consumes(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(
        app, ["add", "contract", "permits", "--version", "v2", "--consumes"]
    )
    assert result.exit_code == 0, result.stderr
    assert (ps_root / "contracts" / "consumed" / "permits.v2.yaml").is_file()


def test_add_contract_requires_one_of(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "contract", "x", "--version", "v1"])
    assert result.exit_code != 0
    assert "exactly one" in result.stderr.lower()


def test_add_contract_rejects_bad_version(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(
        app, ["add", "contract", "x", "--version", "1.0", "--exposes"]
    )
    assert result.exit_code != 0
