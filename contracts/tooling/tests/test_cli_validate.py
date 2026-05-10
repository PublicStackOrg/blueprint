from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from publicstack_contracts.cli import app


def test_validate_each_exemplar_exits_zero(runner: CliRunner, examples_dir: Path) -> None:
    for f in sorted(examples_dir.glob("*.yaml")):
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 0, (f, result.stderr)


def test_validate_unparseable_exit_2(runner: CliRunner, tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(":::not yaml")
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 2


def test_validate_invalid_exit_1(runner: CliRunner, tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("type: object\n")  # JSON Schema, but missing all metadata
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 1


def test_version_subcommand(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "publicstack-contracts" in result.stdout
