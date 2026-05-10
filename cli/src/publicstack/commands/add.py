"""`publicstack add api|app|contract|grid`."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import typer

from publicstack import errors
from publicstack.codegen import slug as slug_mod
from publicstack.codegen.cookiecutter_runner import run as cookiecutter_run
from publicstack.editors import AlreadyApplied
from publicstack.editors.compose import add_service_block
from publicstack.editors.package_json import add_flutter_script
from publicstack.editors.pyproject_root import add_path_dep
from publicstack.paths import add_template_dir, find_public_service_root

add_app = typer.Typer(
    help="Add a piece to the current Public Service.",
    no_args_is_help=True,
)

_RESERVED_SERVICE_NAMES = {"db", "redis", "migrator", "api", "worker"}
_VERSION_RE = re.compile(r"^v[0-9]+$")


def _ps_root_or_die() -> Path:
    try:
        return find_public_service_root()
    except FileNotFoundError as e:
        errors.die(
            str(e),
            "cd into a generated Public Service (one with a BLUEPRINT_VERSION file)",
        )
        raise  # unreachable; satisfies type checkers


@add_app.command("api")
def api_cmd(
    name: str = typer.Argument(..., help="New service name (slug)."),
) -> None:
    """Add a new internal HTTP service under services/<name>."""
    if not slug_mod.is_valid_slug(name):
        errors.die(
            f"'{name}' is not a valid slug",
            "use [a-z][a-z0-9_-]{1,49}",
        )
    if name in _RESERVED_SERVICE_NAMES:
        errors.die(
            f"'{name}' is a reserved compose service name",
            f"avoid: {', '.join(sorted(_RESERVED_SERVICE_NAMES))}",
        )

    root = _ps_root_or_die()
    target = root / "services" / name
    if target.exists():
        errors.die(
            f"services/{name} already exists",
            "pick a different name or remove the existing directory",
        )

    compose = root / "docker-compose.yml"
    pyproject = root / "pyproject.toml"
    for f in (compose, pyproject):
        if not f.is_file():
            errors.die(
                f"missing wiring file: {f}",
                "is this really a generated Public Service?",
            )

    services_dir = root / "services"
    services_dir.mkdir(exist_ok=True)
    with add_template_dir("service") as tdir:
        cookiecutter_run(
            tdir,
            output_dir=services_dir,
            extra_context={
                "service_name": name,
                "python_package": slug_mod.derive_python_package(name),
            },
        )

    try:
        add_service_block(compose, name, kind="api")
        add_path_dep(pyproject, name, path=f"services/{name}", develop=True)
    except AlreadyApplied as e:
        # The new service files were written; surface the issue and roll back
        # the generated tree so the next attempt is clean.
        shutil.rmtree(target, ignore_errors=True)
        errors.die(str(e), "see the message above; resolve and re-run")
        return

    errors.ok(f"added services/{name}")
    typer.echo(
        "  remember to run `poetry lock` and `docker compose build "
        f"{name}` before bringing the stack up.\n"
    )


@add_app.command("app")
def app_cmd(
    name: str = typer.Argument(..., help="New Flutter app name (slug)."),
    kind: str = typer.Option(
        "flutter", "--kind", help="App kind: flutter (default) or web."
    ),
) -> None:
    """Add a new Flutter app under apps/<name>."""
    if kind == "web":
        errors.die(
            "--kind web is not yet implemented in this phase",
            "drop --kind to scaffold a Flutter app, or open an issue",
        )
    if kind != "flutter":
        errors.die(f"unknown --kind: {kind}", "supported kinds: flutter")

    if not slug_mod.is_valid_python_package(name):
        errors.die(
            f"'{name}' is not a valid Flutter package name",
            "use lowercase letters, digits, and underscores only",
        )

    root = _ps_root_or_die()
    target = root / "apps" / name
    if target.exists():
        errors.die(
            f"apps/{name} already exists",
            "pick a different name or remove the existing directory",
        )

    pkg = root / "package.json"
    if not pkg.is_file():
        errors.die(
            f"missing wiring file: {pkg}",
            "is this really a generated Public Service?",
        )

    apps_dir = root / "apps"
    apps_dir.mkdir(exist_ok=True)
    with add_template_dir("app") as tdir:
        cookiecutter_run(
            tdir,
            output_dir=apps_dir,
            extra_context={"app_name": name},
        )

    try:
        add_flutter_script(pkg, name)
    except AlreadyApplied as e:
        shutil.rmtree(target, ignore_errors=True)
        errors.die(str(e), None)
        return

    errors.ok(f"added apps/{name}")
    typer.echo(
        f"  next: cd apps/{name} && flutter pub get; "
        f"then `npm run flutter:{name}`.\n"
    )


@add_app.command("contract")
def contract_cmd(
    name: str = typer.Argument(..., help="Contract name (slug)."),
    version: str = typer.Option(..., "--version", help="Contract version (e.g. v1)."),
    exposes: bool = typer.Option(
        False, "--exposes", help="This Public Service exposes the contract."
    ),
    consumes: bool = typer.Option(
        False, "--consumes", help="This Public Service consumes the contract."
    ),
) -> None:
    """Add a contract schema stub under contracts/{exposed,consumed}/."""
    if exposes == consumes:
        errors.die(
            "specify exactly one of --exposes / --consumes",
            None,
        )
    if not slug_mod.is_valid_slug(name):
        errors.die(f"'{name}' is not a valid slug", None)
    if not _VERSION_RE.match(version):
        errors.die(
            f"'{version}' is not a valid version",
            "use the form v1, v2, ...",
        )

    root = _ps_root_or_die()
    kind_dir = "exposed" if exposes else "consumed"
    out_dir = root / "contracts" / kind_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = out_dir / f"{name}.{version}.yaml"
    if final_path.exists():
        errors.die(f"{final_path} already exists", None)

    # Cookiecutter writes into a directory named after contract_name; the
    # rendered file inside is what we actually want. Move it into place.
    with add_template_dir("contract") as tdir, _scratch_dir() as scratch:
        generated_dir = cookiecutter_run(
            tdir,
            output_dir=scratch,
            extra_context={"contract_name": name, "version": version},
        )
        generated_file = generated_dir / f"{name}.{version}.yaml"
        if not generated_file.exists():
            errors.die(
                f"contract template did not produce {generated_file.name}",
                "this is a CLI bug; please report",
            )
        shutil.move(str(generated_file), str(final_path))

    errors.ok(f"added {final_path.relative_to(root)}")


_GRID_SERVICES = {
    "identity",
    "payments",
    "notifications",
    "audit",
    "document_storage",
    "accessibility",
}


@add_app.command("grid")
def grid_cmd(
    service: str = typer.Argument(..., help="Grid service name."),
) -> None:
    """Wire a Grid service into the current Public Service.

    Idempotent: if `grid/<service>.yaml` already exists, prints `unchanged`
    and exits 0. If the per-PS adapter slot is missing (older PSes that
    pre-date this Grid service), copies the bundled stub into
    `libraries/grid_adapters/grid_adapters/<service>/`.
    """
    if service not in _GRID_SERVICES:
        errors.die(
            f"'{service}' is not a known Grid service",
            f"one of: {', '.join(sorted(_GRID_SERVICES))}",
        )

    root = _ps_root_or_die()
    grid_dir = root / "grid"
    grid_dir.mkdir(exist_ok=True)
    final_yaml = grid_dir / f"{service}.yaml"

    yaml_already = final_yaml.exists()
    adapter_dir = root / "libraries" / "grid_adapters" / "grid_adapters" / service
    adapter_already = adapter_dir.is_dir()

    if yaml_already and adapter_already:
        errors.info(f"grid/{service}.yaml unchanged; adapter slot already present")
        return

    if not yaml_already:
        with add_template_dir("grid") as tdir, _scratch_dir() as scratch:
            generated = cookiecutter_run(
                tdir,
                output_dir=scratch,
                extra_context={"service_name": service},
            )
            generated_yaml = generated / f"{service}.yaml"
            if not generated_yaml.exists():
                errors.die(
                    f"grid template did not produce {generated_yaml.name}",
                    "this is a CLI bug; please report",
                )
            shutil.move(str(generated_yaml), str(final_yaml))
        errors.ok(f"wrote grid/{service}.yaml")

    if not adapter_already:
        # Copy the bundled adapter stub if we have one for this service.
        with add_template_dir("grid") as tdir:
            stub_src = tdir / "_adapter_stubs" / service
            if stub_src.is_dir():
                adapter_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(stub_src, adapter_dir)
                errors.ok(f"scaffolded libraries/grid_adapters/grid_adapters/{service}/")
            else:
                errors.warn(
                    f"no bundled stub for '{service}' adapter; skipping scaffold",
                    "create libraries/grid_adapters/grid_adapters/{service}/__init__.py manually",
                )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

from contextlib import contextmanager  # noqa: E402
from tempfile import TemporaryDirectory  # noqa: E402


@contextmanager
def _scratch_dir():
    with TemporaryDirectory() as d:
        yield Path(d)
