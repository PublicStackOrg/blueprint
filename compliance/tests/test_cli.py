from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from publicstack_compliance.cli import app


def test_version_subcommand(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "publicstack-compliance" in result.stdout


def test_list_checks_lists_six(runner: CliRunner) -> None:
    result = runner.invoke(app, ["list-checks"])
    assert result.exit_code == 0
    expected = {
        "data_export", "contract_compat", "grid_integration",
        "security", "observability", "accessibility",
    }
    listed = set(result.stdout.split())
    assert expected <= listed


def test_run_outside_ps_exits_2(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(app, ["run", "--path", str(tmp_path)])
    assert result.exit_code == 2
    assert "BLUEPRINT_VERSION" in result.stderr


def test_run_with_minimal_ps_returns_info_findings(
    runner: CliRunner, ps_minimal: Path
) -> None:
    """All six checks are stubs in C1 — they emit `info` findings, no
    breaking, so exit code is 0."""
    result = runner.invoke(app, ["run", "--path", str(ps_minimal)])
    assert result.exit_code == 0, result.stderr


def test_run_unknown_check_exits_2(runner: CliRunner, ps_minimal: Path) -> None:
    result = runner.invoke(
        app, ["run", "--path", str(ps_minimal), "--check", "telepathy"]
    )
    assert result.exit_code == 2
    assert "unknown check" in result.stderr.lower()


def test_run_format_json(runner: CliRunner, ps_minimal: Path) -> None:
    result = runner.invoke(
        app, ["run", "--path", str(ps_minimal), "--format", "json"]
    )
    assert result.exit_code == 0
    import json
    parsed = json.loads(result.stdout)
    assert "findings" in parsed
    assert "summary" in parsed
