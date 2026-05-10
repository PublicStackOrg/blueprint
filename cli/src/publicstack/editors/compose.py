"""Round-trip editor for `docker-compose.yml` using ruamel.yaml."""

from __future__ import annotations

from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Literal

from ruamel.yaml import YAML

from publicstack.editors import AlreadyApplied


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 4096
    return y


def add_service_block(
    compose_path: Path,
    name: str,
    *,
    kind: Literal["api", "worker"],
) -> None:
    """Insert a new service block under `services:`, modeled on the existing
    api or worker block. Idempotent: raises AlreadyApplied if `name` is taken."""
    y = _yaml()
    text = compose_path.read_text(encoding="utf-8")
    data = y.load(text)

    services = data.get("services")
    if services is None:
        raise ValueError(f"{compose_path} has no `services:` mapping")
    if name in services:
        raise AlreadyApplied(f"service '{name}' already exists in {compose_path}")

    if kind not in services:
        raise ValueError(
            f"cannot model new service on missing '{kind}' block in {compose_path}"
        )

    block = deepcopy(services[kind])
    # Repoint the Dockerfile path. The build.context stays at `.`.
    if "build" in block and isinstance(block["build"], dict):
        block["build"]["dockerfile"] = f"services/{name}/Dockerfile"
    # Drop any host port bindings — only one service can bind a host port by
    # default; let the operator add an explicit `ports:` entry if needed.
    block.pop("ports", None)

    services[name] = block

    out = StringIO()
    y.dump(data, out)
    compose_path.write_text(out.getvalue(), encoding="utf-8")
