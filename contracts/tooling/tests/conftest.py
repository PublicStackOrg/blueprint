from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "contracts" / "examples"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def examples_dir() -> Path:
    return EXAMPLES_DIR
