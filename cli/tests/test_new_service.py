from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter
from typer.testing import CliRunner

from publicstack.cli import app
from publicstack.paths import blueprint_template_dir, bundled_blueprint_version


def _walk(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel == ".git":
            continue
        files[rel] = p.read_bytes()
    return files


def test_new_service_matches_direct_cookiecutter(
    tmp_path: Path, runner: CliRunner
) -> None:
    """`publicstack new service smoke` produces an identical tree to
    running `cookiecutter` directly against the bundled template."""

    via_cli = tmp_path / "via_cli"
    via_cc = tmp_path / "via_cc"
    via_cli.mkdir()
    via_cc.mkdir()

    result = runner.invoke(
        app,
        ["new", "service", "smoke", "--output-dir", str(via_cli)],
    )
    assert result.exit_code == 0, result.stderr

    extra = {
        "public_service_name": "smoke",
        "public_service_slug": "smoke",
        "python_package": "smoke",
        "description": "An open-source PublicStack Public Service.",
        "github_org": "PublicStackOrg",
        "blueprint_version": bundled_blueprint_version(),
    }
    with blueprint_template_dir() as tdir:
        cookiecutter(
            str(tdir),
            no_input=True,
            output_dir=str(via_cc),
            extra_context=extra,
        )

    cli_tree = _walk(via_cli / "smoke")
    cc_tree = _walk(via_cc / "smoke")

    assert set(cli_tree.keys()) == set(cc_tree.keys())
    diffs = [k for k in cli_tree if cli_tree[k] != cc_tree[k]]
    assert not diffs, f"contents differ in: {diffs}"


def test_new_service_rejects_existing_target(
    tmp_path: Path, runner: CliRunner
) -> None:
    (tmp_path / "smoke").mkdir()
    result = runner.invoke(
        app,
        ["new", "service", "smoke", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "already exists" in result.stderr


def test_new_service_rejects_invalid_slug(
    tmp_path: Path, runner: CliRunner
) -> None:
    result = runner.invoke(
        app,
        ["new", "service", "1bad-name", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "slug" in result.stderr.lower()


@pytest.fixture(autouse=True)
def _isolate_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Stop the post-gen hook from creating real `.git/` directories during
    the parity test, so byte-comparison is stable. Replaced by a no-op git
    binary on PATH."""
    fake_bin = tmp_path / "fakebin"
    fake_bin.mkdir()
    fake_git = fake_bin / "git"
    fake_git.write_text("#!/bin/sh\nexit 0\n")
    fake_git.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:" + str(shutil.os.environ.get("PATH", "")))
