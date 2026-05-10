"""data_export check — every entity model has a working export endpoint
covered by an integration test.

Scope (PLAN.md §6): "every entity defined in libraries/core/models/ has
a working export endpoint covered by an integration test." We treat
classes inheriting `Base` declared in libraries/core/core/db/models.py
(or libraries/core/core/db/models/*.py) as the model set. Filename-driven
detection — deterministic without spinning up a Poetry env.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from publicstack_compliance.findings import Finding

NAME = "data_export"

_BASE_NAMES = {"Base", "DeclarativeBase"}
_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(name: str) -> str:
    """`Citation` -> `citation`. Naive but fine for our names."""
    return _SNAKE.sub("_", name).lower()


def _model_files(ps_root: Path) -> list[Path]:
    """The two filename conventions PublicStack admits."""
    flat = ps_root / "libraries" / "core" / "core" / "db" / "models.py"
    pkg = ps_root / "libraries" / "core" / "core" / "db" / "models"
    files: list[Path] = []
    if flat.is_file():
        files.append(flat)
    if pkg.is_dir():
        files.extend(sorted(pkg.glob("*.py")))
    return files


def _model_classes(path: Path) -> list[str]:
    """Return class names whose direct base is in `_BASE_NAMES`."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    classes: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            base_name = base.id if isinstance(base, ast.Name) else (
                base.attr if isinstance(base, ast.Attribute) else None
            )
            if base_name in _BASE_NAMES:
                classes.append(node.name)
                break
    return classes


def _router_routes(ps_root: Path) -> set[str]:
    """Collect every path-string from `@router.get(...)` / `.post(...)` etc.
    decorators across services/api/api/routers/**/*.py. Returns the *exact*
    decorator strings (e.g. `/items`) plus a "resolved" form that includes
    the parent router prefix when we can statically determine it."""
    routes: set[str] = set()
    routers_dir = ps_root / "services" / "api" / "api" / "routers"
    if not routers_dir.is_dir():
        return routes

    for py in routers_dir.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        # Find APIRouter(prefix="...") assignments to `router` (the convention).
        prefix = ""
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not (
                    isinstance(target, ast.Name)
                    and target.id == "router"
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "APIRouter"
                ):
                    continue
                for kw in node.value.keywords:
                    if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                        prefix = kw.value.value or ""

        # Find every @router.<verb>("...") decorator.
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for dec in node.decorator_list:
                if not (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and isinstance(dec.func.value, ast.Name)
                    and dec.func.value.id == "router"
                    and dec.func.attr in {"get", "post", "put", "delete", "patch", "head"}
                ):
                    continue
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    raw = dec.args[0].value
                    if isinstance(raw, str):
                        routes.add(f"{prefix}{raw}")
                        routes.add(raw)  # also the unprefixed form
    return routes


def _route_uses_streaming(ps_root: Path, expected: str) -> bool:
    """Heuristic: is the function decorated with `@router.<verb>(<expected>)`
    annotated to return `StreamingResponse`? Walks routers/."""
    routers_dir = ps_root / "services" / "api" / "api" / "routers"
    if not routers_dir.is_dir():
        return False
    for py in routers_dir.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for dec in node.decorator_list:
                if not (
                    isinstance(dec, ast.Call)
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                ):
                    continue
                if expected.endswith(dec.args[0].value):
                    ret = node.returns
                    if isinstance(ret, ast.Name) and ret.id == "StreamingResponse":
                        return True
                    if (
                        isinstance(ret, ast.Attribute)
                        and ret.attr == "StreamingResponse"
                    ):
                        return True
    return False


def _has_export_test(ps_root: Path, snake: str) -> bool:
    """True if any tests/test_export*.py mentions the entity name (snake-cased,
    or with naive-plural suffix)."""
    tests_dir = ps_root / "services" / "api" / "tests"
    if not tests_dir.is_dir():
        return False
    needles = (snake, f"{snake}s", f"{snake}es")
    for py in tests_dir.glob("test_export*.py"):
        text = py.read_text(encoding="utf-8")
        if any(n in text for n in needles):
            return True
    return False


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    files = _model_files(ps_root)
    if not files:
        findings.append(Finding(
            check=NAME, rule="DEX-004", severity="warn",
            location="libraries/core/core/db/",
            message="no model files found (expected models.py or models/*.py)",
            suggestion="add libraries/core/core/db/models.py with at least one Base subclass",
        ))
        return findings

    classes: list[tuple[str, Path]] = []
    parse_errors: list[Path] = []
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            parse_errors.append(path)
            continue
        for cls in _model_classes(path):
            classes.append((cls, path))

    for path in parse_errors:
        findings.append(Finding(
            check=NAME, rule="DEX-004", severity="warn",
            location=str(path.relative_to(ps_root)),
            message=f"could not AST-parse {path.name}",
        ))

    if not classes and not parse_errors:
        findings.append(Finding(
            check=NAME, rule="DEX-004", severity="warn",
            location="libraries/core/core/db/",
            message="no model classes found inheriting Base/DeclarativeBase",
        ))
        return findings

    routes = _router_routes(ps_root)

    for cls, model_path in classes:
        snake = _snake(cls)
        # Accept either singular or naive-plural form for the export route.
        # FastAPI convention is plural (/items), but we don't want to be
        # opinionated past "either works."
        candidates = (
            f"/export/{snake}",
            f"/export/{snake}s",
            f"/export/{snake}es",
        )
        has_route = any(
            any(r.endswith(c) for r in routes) for c in candidates
        )
        export_route = next((c for c in candidates
                             if any(r.endswith(c) for r in routes)),
                            f"/export/{snake}s")

        if not has_route:
            findings.append(Finding(
                check=NAME, rule="DEX-001", severity="breaking",
                location=str(model_path.relative_to(ps_root)),
                message=f"{cls} has no /export/{snake}(s) route",
                suggestion=(
                    f"add an APIRouter with @router.get(\"/{snake}s\") under "
                    "services/api/api/routers/v1/export_router.py"
                ),
            ))
            continue

        if not _route_uses_streaming(ps_root, export_route):
            findings.append(Finding(
                check=NAME, rule="DEX-003", severity="info",
                location=str(model_path.relative_to(ps_root)),
                message=(
                    f"{cls}'s export route is not annotated to return "
                    "StreamingResponse; large datasets may load into memory"
                ),
            ))

        if not _has_export_test(ps_root, snake):
            findings.append(Finding(
                check=NAME, rule="DEX-002", severity="warn",
                location=str(model_path.relative_to(ps_root)),
                message=f"{cls} has an export route but no integration test",
                suggestion=(
                    f"add a test under services/api/tests/test_export.py that "
                    f"hits /v1/export/{snake}"
                ),
            ))

    return findings
