"""observability check — structured logs, /metrics, OpenTelemetry tracing.

AST-only static analysis of services/api/api/main.py. We don't run the
service; we look for the right code shapes.

Required:
- Prometheus instrumentator wired with /metrics endpoint
- OpenTelemetry FastAPIInstrumentor.instrument_app()
- python-json-logger JsonFormatter on the root logger
- Unhandled-exception handler `extra={...}` includes request_id, path,
  trace_id, service
"""

from __future__ import annotations

import ast
from pathlib import Path

from publicstack_compliance.findings import Finding

NAME = "observability"

_REQUIRED_LOG_FIELDS = {"request_id", "path", "trace_id", "service"}


def _read_main(ps_root: Path) -> str | None:
    main = ps_root / "services" / "api" / "api" / "main.py"
    if not main.is_file():
        return None
    return main.read_text(encoding="utf-8")


def _has_metrics_expose(text: str) -> bool:
    """Substring match: `Instrumentator(...)` somewhere followed by
    `.expose(` and an `endpoint=` argument referencing /metrics."""
    return "Instrumentator" in text and ".expose(" in text and "/metrics" in text


def _has_otel_instrument(text: str) -> bool:
    return "FastAPIInstrumentor" in text and "instrument_app" in text


def _has_json_formatter(text: str) -> bool:
    """Either `pythonjsonlogger.jsonlogger.JsonFormatter` or
    `pythonjsonlogger.JsonFormatter` (newer single-module form)."""
    return (
        "pythonjsonlogger" in text
        and "JsonFormatter" in text
    )


def _exception_handler_extras(text: str) -> set[str]:
    """Walk the module AST. Look for any `logger.<level>(... extra={...})`
    call inside an exception handler (try/except). Return the set of literal
    string keys passed in `extra=`."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()

    seen: set[str] = set()

    class _Visitor(ast.NodeVisitor):
        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                # Logger calls: looks like a method call.
                func = child.func
                method_name = (
                    func.attr if isinstance(func, ast.Attribute) else None
                )
                if method_name not in {"info", "warn", "warning", "error", "exception", "critical"}:
                    continue
                for kw in child.keywords:
                    if kw.arg == "extra" and isinstance(kw.value, ast.Dict):
                        for k in kw.value.keys:
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                seen.add(k.value)
            self.generic_visit(node)

    # Also walk @app.exception_handler(...) decorated functions which aren't
    # inside try/except but ARE handlers.
    class _DecoratedHandlerVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            self._maybe(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
            self._maybe(node)

        def _maybe(self, node):
            for dec in node.decorator_list:
                ok = (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "exception_handler"
                )
                if not ok:
                    continue
                for child in ast.walk(node):
                    if not isinstance(child, ast.Call):
                        continue
                    for kw in child.keywords:
                        if kw.arg == "extra" and isinstance(kw.value, ast.Dict):
                            for k in kw.value.keys:
                                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                    seen.add(k.value)

    _Visitor().visit(tree)
    _DecoratedHandlerVisitor().visit(tree)
    return seen


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = _read_main(ps_root)
    if text is None:
        findings.append(Finding(
            check=NAME, rule="OBS-001", severity="breaking",
            location="services/api/api/main.py",
            message="services/api/api/main.py not found",
        ))
        return findings

    if not _has_metrics_expose(text):
        findings.append(Finding(
            check=NAME, rule="OBS-001", severity="breaking",
            location="services/api/api/main.py",
            message="no Prometheus /metrics endpoint detected",
            suggestion=(
                "use prometheus-fastapi-instrumentator: "
                "`Instrumentator().instrument(app).expose(app, endpoint='/metrics')`"
            ),
        ))

    if not _has_otel_instrument(text):
        findings.append(Finding(
            check=NAME, rule="OBS-002", severity="breaking",
            location="services/api/api/main.py",
            message="no OpenTelemetry FastAPI instrumentation detected",
            suggestion=(
                "add `FastAPIInstrumentor().instrument_app(app)` after creating "
                "the app"
            ),
        ))

    if not _has_json_formatter(text):
        findings.append(Finding(
            check=NAME, rule="OBS-003", severity="breaking",
            location="services/api/api/main.py",
            message="no python-json-logger JsonFormatter detected on the root logger",
            suggestion=(
                "configure logging with `pythonjsonlogger.JsonFormatter` so "
                "structured-log fields are emitted as JSON"
            ),
        ))

    extras = _exception_handler_extras(text)
    missing = _REQUIRED_LOG_FIELDS - extras
    if missing:
        findings.append(Finding(
            check=NAME, rule="OBS-004", severity="warn",
            location="services/api/api/main.py",
            message=(
                f"unhandled-exception logger missing required fields in "
                f"extra=: {sorted(missing)}"
            ),
            suggestion=(
                "include request_id, path, trace_id, service keys when logging "
                "from the exception handler"
            ),
        ))

    return findings
