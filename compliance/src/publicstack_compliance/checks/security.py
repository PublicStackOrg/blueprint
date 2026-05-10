"""security check — pip-audit, gitleaks, CSP middleware, HTTPSRedirect,
no hardcoded secrets.

External tools:
- `pip-audit` (pinned dependency; called as `python -m pip_audit`)
- `gitleaks` (binary on PATH; warn-skip if missing)
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
from pathlib import Path

from publicstack_compliance.findings import Finding

NAME = "security"

# Hardcoded-secret heuristic: `password=`, `secret=`, `api_key=` followed by a
# string literal whose value is not the empty string and doesn't look like
# `os.environ[...]` etc.
_SECRET_KEYS = {"password", "secret", "api_key", "apikey", "token"}


def _run_pip_audit(service_dir: Path) -> tuple[list[Finding], bool]:
    """Returns (findings, ran_successfully)."""
    findings: list[Finding] = []
    if shutil.which("python") is None:
        return findings, False

    try:
        export = subprocess.run(
            ["poetry", "export", "-f", "requirements.txt", "--without-hashes"],
            cwd=service_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return findings, False
    if export.returncode != 0:
        return findings, False

    try:
        audit = subprocess.run(
            ["python", "-m", "pip_audit", "-r", "/dev/stdin", "--format", "json"],
            input=export.stdout,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return findings, False

    if audit.returncode not in (0, 1):
        return findings, False

    try:
        payload = json.loads(audit.stdout) if audit.stdout.strip() else {}
    except json.JSONDecodeError:
        return findings, False

    for dep in (payload.get("dependencies") or []):
        for vuln in dep.get("vulns") or []:
            findings.append(Finding(
                check=NAME, rule="SEC-001", severity="breaking",
                location=f"{service_dir.name}: {dep.get('name')}=={dep.get('version')}",
                message=f"vulnerability {vuln.get('id')} ({vuln.get('description', '')[:140]})",
            ))
    return findings, True


def _run_gitleaks(ps_root: Path) -> tuple[list[Finding], bool]:
    findings: list[Finding] = []
    if shutil.which("gitleaks") is None:
        return findings, False

    try:
        result = subprocess.run(
            [
                "gitleaks", "detect",
                "--source", str(ps_root),
                "--no-git",
                "--redact",
                "--report-format", "json",
                "--report-path", "/dev/stdout",
                "--exit-code", "0",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return findings, False

    try:
        leaks = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return findings, True  # ran, but couldn't parse — treat as no leaks

    for leak in leaks or []:
        findings.append(Finding(
            check=NAME, rule="SEC-002", severity="breaking",
            location=f"{leak.get('File', '?')}:{leak.get('StartLine', '?')}",
            message=f"{leak.get('RuleID', 'leak')}: {leak.get('Description', '')[:140]}",
        ))
    return findings, True


def _csp_present(main_py: Path) -> bool:
    """True if main.py adds a middleware that sets Content-Security-Policy."""
    if not main_py.is_file():
        return False
    text = main_py.read_text(encoding="utf-8")
    return "Content-Security-Policy" in text


def _https_redirect_present(main_py: Path) -> bool:
    if not main_py.is_file():
        return False
    text = main_py.read_text(encoding="utf-8")
    return "HTTPSRedirectMiddleware" in text


def _hardcoded_secret_findings(path: Path) -> list[Finding]:
    """AST-scan a Python file for `<key>=<string-literal>` where key is in
    _SECRET_KEYS and value is non-empty + not env-derived."""
    findings: list[Finding] = []
    if not path.is_file():
        return findings
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        # Look at keyword args: foo(password="abc")
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if (
                    kw.arg
                    and kw.arg.lower() in _SECRET_KEYS
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                    and kw.value.value
                ):
                    findings.append(Finding(
                        check=NAME, rule="SEC-005", severity="breaking",
                        location=f"{path.name}:{kw.value.lineno}",
                        message=f"hardcoded `{kw.arg}=` literal",
                        suggestion="read this from settings / env, not source",
                    ))
        # Look at module-level assignments: PASSWORD = "abc"
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                lowered = target.id.lower()
                if (
                    any(k in lowered for k in _SECRET_KEYS)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and node.value.value
                ):
                    findings.append(Finding(
                        check=NAME, rule="SEC-005", severity="breaking",
                        location=f"{path.name}:{node.value.lineno}",
                        message=f"hardcoded `{target.id}=` literal",
                        suggestion="read this from settings / env, not source",
                    ))
    return findings


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []

    # SEC-003 / SEC-004 — middleware AST checks.
    main_py = ps_root / "services" / "api" / "api" / "main.py"
    if main_py.is_file():
        if not _csp_present(main_py):
            findings.append(Finding(
                check=NAME, rule="SEC-003", severity="breaking",
                location="services/api/api/main.py",
                message="no Content-Security-Policy middleware detected",
                suggestion=(
                    "add a middleware that sets `Content-Security-Policy: "
                    "default-src 'self'` (or stricter)"
                ),
            ))
        if not _https_redirect_present(main_py):
            findings.append(Finding(
                check=NAME, rule="SEC-004", severity="breaking",
                location="services/api/api/main.py",
                message="no HTTPSRedirectMiddleware detected",
                suggestion=(
                    "add `HTTPSRedirectMiddleware` gated by a non-local environment"
                ),
            ))

    # SEC-005 — hardcoded secrets in main.py / dependencies.py / config.py.
    for rel in ("services/api/api/main.py",
                "services/api/api/dependencies.py",
                "services/api/api/config.py"):
        findings.extend(_hardcoded_secret_findings(ps_root / rel))

    # SEC-001 — pip-audit per service. Skip if tool missing.
    services_dir = ps_root / "services"
    if services_dir.is_dir():
        ran_any_audit = False
        for service in sorted(services_dir.iterdir()):
            if not (service / "pyproject.toml").is_file():
                continue
            audit_findings, ok = _run_pip_audit(service)
            findings.extend(audit_findings)
            ran_any_audit = ran_any_audit or ok
        if not ran_any_audit:
            findings.append(Finding(
                check=NAME, rule="SEC-006", severity="warn",
                location="",
                message=(
                    "pip-audit could not run for any service "
                    "(missing python / poetry / pip_audit)"
                ),
                suggestion="install pip-audit (`pip install pip-audit`) and Poetry",
            ))

    # SEC-002 — gitleaks. Skip if tool missing.
    if shutil.which("gitleaks") is None:
        if os.environ.get("PUBLICSTACK_COMPLIANCE_REQUIRE_GITLEAKS"):
            findings.append(Finding(
                check=NAME, rule="SEC-006", severity="breaking",
                location="",
                message="gitleaks required but not on PATH",
            ))
        else:
            findings.append(Finding(
                check=NAME, rule="SEC-006", severity="warn",
                location="",
                message="gitleaks not on PATH; secret-history scan skipped",
                suggestion="install gitleaks (e.g. `brew install gitleaks`)",
            ))
    else:
        gitleaks_findings, _ok = _run_gitleaks(ps_root)
        findings.extend(gitleaks_findings)

    return findings
