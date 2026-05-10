from __future__ import annotations

from typer.testing import CliRunner

from publicstack import __version__
from publicstack.cli import app
from publicstack.paths import bundled_blueprint_version


def test_version_prints_cli_and_blueprint(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, result.stderr
    assert f"publicstack {__version__}" in result.stdout
    assert f"blueprint   {bundled_blueprint_version()}" in result.stdout
