"""accessibility check — axe-core via Playwright against each Flutter web build.

Flow per app under apps/*/ :
1. Look for a built `build/web/index.html`. Absent → A11Y-005 info, skip.
2. Probe Playwright Chromium availability. Missing → A11Y-006 warn, skip.
3. Serve `build/web/` over a random localhost port via http.server,
   navigate Playwright Chromium to it, inject the bundled axe.min.js,
   call axe.run(), parse violations.
4. Map axe-core severities to A11Y-001..004.

The check is opt-in heavy: pipx-only installs without a browser still
get all the other checks; only this one warn-skips.
"""

from __future__ import annotations

import http.server
import socket
import socketserver
import threading
from importlib import resources
from pathlib import Path

from publicstack_compliance.findings import Finding

NAME = "accessibility"

_SEVERITY_MAP = {
    "critical": ("A11Y-001", "breaking"),
    "serious": ("A11Y-002", "breaking"),
    "moderate": ("A11Y-003", "warn"),
    "minor": ("A11Y-004", "info"),
}


def _axe_script() -> str:
    return resources.files("publicstack_compliance").joinpath(
        "_vendor", "axe.min.js"
    ).read_text(encoding="utf-8")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve(directory: Path, port: int) -> socketserver.TCPServer:
    handler = http.server.SimpleHTTPRequestHandler

    class _Handler(handler):  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, *_a, **_k) -> None:  # silence stdout
            pass

    server = socketserver.TCPServer(("127.0.0.1", port), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _playwright_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except Exception:
        return False
    return True


def _scan_app(app_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    web_index = app_dir / "build" / "web" / "index.html"
    if not web_index.is_file():
        findings.append(Finding(
            check=NAME, rule="A11Y-005", severity="info",
            location=str(app_dir.name),
            message=f"no Flutter web build at apps/{app_dir.name}/build/web/",
            suggestion=(
                f"`cd apps/{app_dir.name} && flutter build web --release` "
                "before running the a11y check"
            ),
        ))
        return findings

    if not _playwright_available():
        findings.append(Finding(
            check=NAME, rule="A11Y-006", severity="warn",
            location="",
            message="Playwright not installed — accessibility scan skipped",
            suggestion="run `playwright install chromium`",
        ))
        return findings

    from playwright.sync_api import sync_playwright

    port = _free_port()
    server = _serve(web_index.parent, port)
    try:
        try:
            with sync_playwright() as pw:
                try:
                    browser = pw.chromium.launch(headless=True)
                except Exception:
                    findings.append(Finding(
                        check=NAME, rule="A11Y-006", severity="warn",
                        location="",
                        message=(
                            "Playwright chromium not available — "
                            "accessibility scan skipped"
                        ),
                        suggestion="run `playwright install chromium`",
                    ))
                    return findings
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{port}/")
                page.wait_for_load_state("networkidle")
                page.add_script_tag(content=_axe_script())
                results = page.evaluate("axe.run()")
                browser.close()
        finally:
            server.shutdown()
    finally:
        server.server_close()

    for v in results.get("violations") or []:
        impact = (v.get("impact") or "minor").lower()
        rule_id, severity = _SEVERITY_MAP.get(impact, ("A11Y-004", "info"))
        nodes = v.get("nodes") or []
        first_target = ""
        if nodes and isinstance(nodes[0].get("target"), list) and nodes[0]["target"]:
            first_target = str(nodes[0]["target"][0])
        findings.append(Finding(
            check=NAME, rule=rule_id, severity=severity,
            location=f"apps/{app_dir.name} {first_target}",
            message=f"{v.get('id')}: {v.get('help', v.get('description', ''))}",
            suggestion=v.get("helpUrl"),
        ))

    return findings


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    apps_dir = ps_root / "apps"
    if not apps_dir.is_dir():
        return findings
    for app in sorted(apps_dir.iterdir()):
        if not app.is_dir():
            continue
        findings.extend(_scan_app(app))
    return findings
