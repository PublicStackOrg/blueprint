"""Editor for the workspace root package.json using stdlib json."""

from __future__ import annotations

import json
from pathlib import Path

from publicstack.editors import AlreadyApplied


def add_flutter_script(pkg_path: Path, app_name: str) -> None:
    """Add `"flutter:<app_name>": "./scripts/flutter-run.sh <app_name>"` to
    the scripts table. Idempotent: raises AlreadyApplied if already present."""
    text = pkg_path.read_text(encoding="utf-8")
    data = json.loads(text)

    scripts = data.setdefault("scripts", {})
    key = f"flutter:{app_name}"
    if key in scripts:
        raise AlreadyApplied(f"script '{key}' already exists in {pkg_path}")

    scripts[key] = f"./scripts/flutter-run.sh {app_name}"

    pkg_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
