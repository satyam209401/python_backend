from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path
from typing import Any
from fastapi import APIRouter


def auto_sync_routes(
    target_router: APIRouter | None = None,
    routes_dir: str | Path = "routes",
) -> list[dict[str, Any]]:
    """
    Recursively scans the routes directory and mounts all APIRouter instances
    onto the target APIRouter (defaults to builtins.entry).

    Folder/File Structure mapping:
      routes/auth.py             -> Prefix: /auth        Tag: Auth
      routes/user/login.py        -> Prefix: /user/login  Tag: User
      routes/user/index.py        -> Prefix: /user        Tag: User
      routes/index.py             -> Prefix: ""           Tag: Default
    """
    if target_router is None:
        target_router = getattr(builtins, "entry", None)
        if target_router is None:
            return []

    project_root = Path(__file__).resolve().parent.parent.parent
    base_path = Path(routes_dir)
    if not base_path.is_absolute():
        candidate = (project_root / routes_dir).resolve()
        if candidate.exists():
            base_path = candidate
        else:
            base_path = (Path.cwd() / routes_dir).resolve()

    if not base_path.exists() or not base_path.is_dir():
        return []

    # Target router par duplicate inclusions rokne ke liye tracking set
    if not hasattr(target_router, "_synced_route_files"):
        target_router._synced_route_files = set()  # type: ignore[attr-defined]

    synced_records: list[dict[str, Any]] = []

    # Sare .py files ko alphabetically sort karke scan karein
    py_files = sorted(base_path.rglob("*.py"))

    for file_path in py_files:
        # Hidden ya private files / folders (__pycache__, __init__.py wagera) ignore karein
        if file_path.name.startswith((".", "_")):
            continue
        if any(part.startswith((".", "_")) for part in file_path.parts):
            continue

        # Khali file (0 bytes) ko bina error ignore karein
        try:
            if file_path.stat().st_size == 0:
                continue
        except OSError:
            continue

        canonical_file = str(file_path.resolve())
        if canonical_file in target_router._synced_route_files:  # type: ignore[attr-defined]
            continue

        # Relative path se prefix calculate karein
        rel_path = file_path.relative_to(base_path).with_suffix("").as_posix()
        parts = [p for p in rel_path.split("/") if p]
        if not parts:
            continue

        # Agar file 'index.py' hai toh endpoint root hoga
        if parts[-1].lower() == "index":
            route_parts = parts[:-1]
        else:
            route_parts = parts

        computed_prefix = "/" + "/".join(route_parts) if route_parts else ""
        default_tag = parts[0].capitalize() if parts else "API"

        module_name = f"routes_auto_{'_'.join(parts)}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Module me APIRouter find karein
            router_obj = getattr(module, "router", None)
            if not isinstance(router_obj, APIRouter):
                for attr_name, attr_val in vars(module).items():
                    if isinstance(attr_val, APIRouter) and attr_name != "target_router":
                        router_obj = attr_val
                        break

            if router_obj is None or not isinstance(router_obj, APIRouter):
                continue

            # Prefix handling: agar router me pehle se custom prefix hai
            final_prefix = router_obj.prefix if router_obj.prefix else computed_prefix
            tags = router_obj.tags if router_obj.tags else [default_tag]

            # Target router me include karein
            target_router.include_router(router_obj, prefix=final_prefix, tags=tags)
            target_router._synced_route_files.add(canonical_file)  # type: ignore[attr-defined]

            synced_records.append(
                {
                    "file": str(file_path.relative_to(base_path)),
                    "module": module_name,
                    "prefix": final_prefix,
                    "tags": tags,
                    "routes": len(router_obj.routes),
                }
            )
        except Exception as e:
            if hasattr(builtins, "log"):
                builtins.log(f"[AutoRouter] Error loading {file_path}: {e}")
            else:
                print(f"[AutoRouter] Error loading {file_path}: {e}")

    return synced_records


def sync_routes(
    target_router: APIRouter | None = None,
    routes_dir: str | Path = "routes",
) -> list[dict[str, Any]]:
    """
    Public helper to manually trigger route synchronization.
    """
    return auto_sync_routes(target_router=target_router, routes_dir=routes_dir)
