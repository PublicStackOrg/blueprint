"""grid_integration check — every Grid service is wired correctly.

For each `grid/<service>.yaml`:
  - The YAML has `backend:` set
  - The matching adapter package under
    `libraries/grid_adapters/grid_adapters/<service>/__init__.py` exists
    and exports a `*Adapter` class
  - `services/api/api/dependencies.py` defines `get_<service>_adapter`

Required services (always): identity, audit. Recommended (warn-only):
notifications, document_storage, accessibility. Payments is required only
if it's "detected" — heuristic: any model has a column named amount/fee/price.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

from publicstack_compliance.findings import Finding

NAME = "grid_integration"

_REQUIRED = {"identity", "audit"}
_RECOMMENDED = {"notifications", "document_storage", "accessibility"}
_OPTIONAL_DETECTED = {"payments"}
_KNOWN = _REQUIRED | _RECOMMENDED | _OPTIONAL_DETECTED

# Per-service backend allowlists. Each PS can extend this in its own check
# config, but for now we encode the plan's defaults.
_BACKENDS = {
    "identity": {"none", "keycloak", "zitadel", "authentik", "auth0", "clerk", "cognito"},
    "payments": {"log_only", "stripe", "local_bank", "city_merchant"},
    "notifications": {"log_only", "ses", "postmark", "smtp", "twilio", "fcm"},
    "audit": {"postgres", "qldb", "s3_object_lock"},
    "document_storage": {"local", "s3", "gcs", "r2", "azure_blob", "minio"},
    "accessibility": {"in_memory"},
}

_PAYMENT_FIELD_RE = re.compile(r"\b(amount|fee|price|amount_cents)\b")


def _payment_detected(ps_root: Path) -> bool:
    models = ps_root / "libraries" / "core" / "core" / "db" / "models.py"
    if not models.is_file():
        return False
    return bool(_PAYMENT_FIELD_RE.search(models.read_text(encoding="utf-8")))


def _adapter_exports(ps_root: Path, service: str) -> bool:
    """True if libraries/grid_adapters/grid_adapters/<service>/__init__.py
    exports at least one class whose name ends with 'Adapter'."""
    init = (
        ps_root
        / "libraries" / "grid_adapters" / "grid_adapters" / service / "__init__.py"
    )
    if not init.is_file():
        return False
    try:
        tree = ast.parse(init.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    return any(
        isinstance(n, ast.ClassDef) and n.name.endswith("Adapter")
        for n in tree.body
    )


def _has_dependency(ps_root: Path, service: str) -> bool:
    """True if services/api/api/dependencies.py defines `get_<service>_adapter`."""
    deps = ps_root / "services" / "api" / "api" / "dependencies.py"
    if not deps.is_file():
        return False
    try:
        tree = ast.parse(deps.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    target = f"get_{service}_adapter"
    return any(
        isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and n.name == target
        for n in ast.walk(tree)
    )


def _load_grid_yaml(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def run(ps_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    grid_dir = ps_root / "grid"
    payments_required = _payment_detected(ps_root)

    for service in sorted(_KNOWN):
        is_required = (
            service in _REQUIRED
            or (service == "payments" and payments_required)
        )
        severity_for_missing = "breaking" if is_required else "warn"

        yaml_path = grid_dir / f"{service}.yaml"
        if not yaml_path.is_file():
            findings.append(Finding(
                check=NAME, rule="GRD-001", severity=severity_for_missing,
                location=f"grid/{service}.yaml",
                message=f"missing grid/{service}.yaml",
                suggestion=f"run `publicstack add grid {service}`",
            ))
            continue

        data = _load_grid_yaml(yaml_path)
        if data is None or "backend" not in data:
            findings.append(Finding(
                check=NAME, rule="GRD-002", severity="breaking",
                location=f"grid/{service}.yaml",
                message="grid YAML missing required `backend:` field",
            ))
            continue

        backend = data["backend"]
        allowed = _BACKENDS.get(service, set())
        if allowed and backend not in allowed:
            findings.append(Finding(
                check=NAME, rule="GRD-002", severity="breaking",
                location=f"grid/{service}.yaml",
                message=(
                    f"backend={backend!r} not in allowlist for {service}: "
                    f"{sorted(allowed)}"
                ),
            ))

        # Adapter package present + exports a *Adapter class.
        if not _adapter_exports(ps_root, service):
            findings.append(Finding(
                check=NAME, rule="GRD-003", severity=severity_for_missing,
                location=(
                    f"libraries/grid_adapters/grid_adapters/{service}/__init__.py"
                ),
                message=f"adapter package for '{service}' missing or has no *Adapter class",
            ))

        # Dependency wired.
        if not _has_dependency(ps_root, service):
            findings.append(Finding(
                check=NAME, rule="GRD-004", severity="warn",
                location="services/api/api/dependencies.py",
                message=f"no get_{service}_adapter dependency wired",
                suggestion=(
                    f"add `def get_{service}_adapter(...)` mirroring "
                    "the get_identity_adapter pattern"
                ),
            ))

    if payments_required and not (grid_dir / "payments.yaml").is_file():
        findings.append(Finding(
            check=NAME, rule="GRD-005", severity="warn",
            location="grid/",
            message=(
                "models look like they handle money (amount/fee/price columns) "
                "but no grid/payments.yaml exists"
            ),
            suggestion=(
                "run `publicstack add grid payments`, or set backend=none if "
                "this PS doesn't actually take money"
            ),
        ))

    return findings
