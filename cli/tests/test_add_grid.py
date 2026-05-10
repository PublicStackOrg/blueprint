from __future__ import annotations

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
    # Pre-create the grid_adapters/grid_adapters/identity slot so the
    # adapter-already-present branch is exercised.
    adapter_dir = root / "libraries" / "grid_adapters" / "grid_adapters" / "identity"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "__init__.py").write_text("# stub\n")
    monkeypatch.chdir(root)
    return root


def test_add_grid_identity_writes_yaml(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "grid", "identity"])
    assert result.exit_code == 0, result.stderr
    yaml_path = ps_root / "grid" / "identity.yaml"
    assert yaml_path.is_file()
    content = yaml_path.read_text()
    assert "backend: none" in content


def test_add_grid_idempotent(ps_root: Path, runner: CliRunner) -> None:
    runner.invoke(app, ["add", "grid", "identity"])
    result = runner.invoke(app, ["add", "grid", "identity"])
    assert result.exit_code == 0
    assert "unchanged" in result.stderr


def test_add_grid_audit_scaffolds_missing_adapter(
    ps_root: Path, runner: CliRunner
) -> None:
    # Fixture has no adapter slot for `audit`; the command should copy the
    # bundled stub.
    audit_dir = ps_root / "libraries" / "grid_adapters" / "grid_adapters" / "audit"
    assert not audit_dir.exists()

    result = runner.invoke(app, ["add", "grid", "audit"])
    assert result.exit_code == 0, result.stderr
    assert (ps_root / "grid" / "audit.yaml").is_file()
    assert (audit_dir / "__init__.py").is_file()


def test_add_grid_unknown_service_fails(ps_root: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["add", "grid", "telepathy"])
    assert result.exit_code != 0
    assert "not a known Grid service" in result.stderr


def test_add_grid_outside_ps(
    tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["add", "grid", "identity"])
    assert result.exit_code != 0
    assert "BLUEPRINT_VERSION" in result.stderr
