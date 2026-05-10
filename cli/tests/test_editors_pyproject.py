from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import tomlkit

from publicstack.editors import AlreadyApplied
from publicstack.editors.pyproject_root import add_path_dep

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps" / "pyproject.toml"


@pytest.fixture()
def pyproject(tmp_path: Path) -> Path:
    dst = tmp_path / "pyproject.toml"
    shutil.copy(FIXTURE, dst)
    return dst


def test_add_path_dep_inserts_table(pyproject: Path) -> None:
    add_path_dep(pyproject, "scrubber", path="services/scrubber")
    doc = tomlkit.parse(pyproject.read_text())
    deps = doc["tool"]["poetry"]["dependencies"]
    assert "scrubber" in deps
    assert deps["scrubber"]["path"] == "services/scrubber"
    assert deps["scrubber"]["develop"] is True


def test_add_path_dep_idempotent(pyproject: Path) -> None:
    add_path_dep(pyproject, "scrubber", path="services/scrubber")
    with pytest.raises(AlreadyApplied):
        add_path_dep(pyproject, "scrubber", path="services/scrubber")


def test_add_path_dep_preserves_existing(pyproject: Path) -> None:
    add_path_dep(pyproject, "scrubber", path="services/scrubber")
    doc = tomlkit.parse(pyproject.read_text())
    deps = doc["tool"]["poetry"]["dependencies"]
    assert "api" in deps and "worker" in deps and "core" in deps
