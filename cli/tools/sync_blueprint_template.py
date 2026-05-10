#!/usr/bin/env python3
"""Sync blueprint/template/ → blueprint/cli/src/publicstack/templates/_blueprint/.

The CLI bundles the cookiecutter template inside its wheel so it works
regardless of install path. This script keeps the bundled copy in sync
with the source-of-truth `blueprint/template/` tree.

Usage:
  python tools/sync_blueprint_template.py          # write/update the bundled copy
  python tools/sync_blueprint_template.py --check  # exit 1 if a sync is needed
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]  # blueprint/cli/
BLUEPRINT_ROOT = REPO_ROOT.parent  # blueprint/
SOURCE = BLUEPRINT_ROOT / "template"  # blueprint/template/
VERSION_SRC = BLUEPRINT_ROOT / "VERSION"  # blueprint/VERSION
DEST = REPO_ROOT / "src" / "publicstack" / "templates" / "_blueprint"
VERSION_DEST = REPO_ROOT / "src" / "publicstack" / "templates" / "_blueprint_version"


_IGNORE = (".ruff_cache", "__pycache__", ".pytest_cache", ".mypy_cache", ".DS_Store")


def _trees_equal(a: Path, b: Path) -> bool:
    if not (a.is_dir() and b.is_dir()):
        return False
    cmp = filecmp.dircmp(a, b, ignore=list(_IGNORE))
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    for sub in cmp.common_dirs:
        if not _trees_equal(a / sub, b / sub):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the bundled copy is out of sync with the source.",
    )
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"source missing: {SOURCE}", file=sys.stderr)
        return 1
    if not VERSION_SRC.exists():
        print(f"VERSION missing: {VERSION_SRC}", file=sys.stderr)
        return 1

    if args.check:
        version_match = (
            VERSION_DEST.exists()
            and VERSION_DEST.read_text() == VERSION_SRC.read_text()
        )
        tree_match = DEST.exists() and _trees_equal(SOURCE, DEST)
        if not (version_match and tree_match):
            print(
                f"bundled blueprint template is out of sync.\n"
                f"  source: {SOURCE} (+ {VERSION_SRC})\n"
                f"  dest:   {DEST} (+ {VERSION_DEST})\n"
                f"  fix: run `python {Path(__file__).relative_to(REPO_ROOT)}`",
                file=sys.stderr,
            )
            return 1
        return 0

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, DEST, ignore=shutil.ignore_patterns(*_IGNORE))
    shutil.copyfile(VERSION_SRC, VERSION_DEST)
    print(f"synced {SOURCE} → {DEST}")
    print(f"synced {VERSION_SRC} → {VERSION_DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
