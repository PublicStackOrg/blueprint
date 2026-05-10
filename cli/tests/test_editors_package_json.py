from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from publicstack.editors import AlreadyApplied
from publicstack.editors.package_json import add_flutter_script

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps" / "package.json"


@pytest.fixture()
def pkg(tmp_path: Path) -> Path:
    dst = tmp_path / "package.json"
    shutil.copy(FIXTURE, dst)
    return dst


def test_add_flutter_script(pkg: Path) -> None:
    add_flutter_script(pkg, "inspector")
    data = json.loads(pkg.read_text())
    assert data["scripts"]["flutter:inspector"] == "./scripts/flutter-run.sh inspector"
    # Existing keys preserved.
    assert "flutter:resident" in data["scripts"]


def test_add_flutter_script_idempotent(pkg: Path) -> None:
    add_flutter_script(pkg, "inspector")
    with pytest.raises(AlreadyApplied):
        add_flutter_script(pkg, "inspector")


def test_add_flutter_script_preserves_indentation(pkg: Path) -> None:
    add_flutter_script(pkg, "inspector")
    text = pkg.read_text()
    assert text.endswith("\n")
    # Two-space indent for top-level keys.
    assert '  "scripts":' in text
