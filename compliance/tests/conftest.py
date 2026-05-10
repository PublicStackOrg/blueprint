from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture()
def ps_minimal(tmp_path: Path) -> Path:
    """Copy the bundled minimal PS fixture into a writable tmp_path."""
    import shutil

    src = FIXTURES / "ps_minimal"
    dst = tmp_path / "ps"
    shutil.copytree(src, dst)
    return dst
