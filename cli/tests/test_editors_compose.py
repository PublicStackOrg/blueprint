from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from publicstack.editors import AlreadyApplied
from publicstack.editors.compose import add_service_block

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_ps" / "docker-compose.yml"


@pytest.fixture()
def compose_path(tmp_path: Path) -> Path:
    dst = tmp_path / "docker-compose.yml"
    shutil.copy(FIXTURE, dst)
    return dst


def _load(p: Path) -> dict:
    return YAML().load(p.read_text())


def test_add_service_block_inserts_under_services(compose_path: Path) -> None:
    add_service_block(compose_path, "scrubber", kind="api")
    data = _load(compose_path)
    assert "scrubber" in data["services"]
    assert data["services"]["scrubber"]["build"]["dockerfile"] == (
        "services/scrubber/Dockerfile"
    )
    # ports should NOT be carried over from the api block.
    assert "ports" not in data["services"]["scrubber"]


def test_add_service_block_preserves_comments(compose_path: Path) -> None:
    before = compose_path.read_text()
    assert "# minimal_ps — fixture" in before
    add_service_block(compose_path, "scrubber", kind="api")
    after = compose_path.read_text()
    assert "# minimal_ps — fixture" in after


def test_add_service_block_idempotent(compose_path: Path) -> None:
    add_service_block(compose_path, "scrubber", kind="api")
    with pytest.raises(AlreadyApplied):
        add_service_block(compose_path, "scrubber", kind="api")
