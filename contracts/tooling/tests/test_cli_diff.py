from __future__ import annotations

import shutil
from pathlib import Path

import yaml
from typer.testing import CliRunner

from publicstack_contracts.cli import app


def test_diff_identical_exit_zero(runner: CliRunner, examples_dir: Path) -> None:
    f = examples_dir / "citations.v1.yaml"
    result = runner.invoke(app, ["diff", str(f), str(f)])
    assert result.exit_code == 0, result.stderr


def test_diff_removed_required_exit_one(
    runner: CliRunner, examples_dir: Path, tmp_path: Path
) -> None:
    src = examples_dir / "audit_entry.v1.yaml"
    v1 = tmp_path / "audit.v1.yaml"
    v2 = tmp_path / "audit.v2.yaml"
    shutil.copy(src, v1)
    doc = yaml.safe_load(src.read_text())
    # Remove `id` from required + delete it from properties — JS001.
    doc["required"].remove("id")
    doc["properties"].pop("id")
    v2.write_text(yaml.safe_dump(doc, sort_keys=False))

    result = runner.invoke(app, ["diff", str(v1), str(v2)])
    assert result.exit_code == 1
    assert "JS001" in result.stdout


def test_diff_format_mismatch_exit_two(
    runner: CliRunner, examples_dir: Path
) -> None:
    a = examples_dir / "citations.v1.yaml"          # openapi
    b = examples_dir / "audit_entry.v1.yaml"        # jsonschema
    result = runner.invoke(app, ["diff", str(a), str(b)])
    assert result.exit_code == 2
    assert "format mismatch" in result.stderr.lower()
