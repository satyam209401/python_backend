import os
import shutil
import sys
from pathlib import Path

# Python ko naye bytecode (.pyc / __pycache__) likhne se rokein
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def clear_pycache(project_dir: str | Path = ".") -> dict[str, int]:
    """
    Project directory me se sabhi __pycache__ folders aur .pyc/.pyo files ko remove karta hai,
    aur project modules ko sys.modules se clear karta hai (excluding .venv).
    """
    project_path = Path(project_dir).resolve()
    exclude = {".venv", "venv", ".git", ".idea", ".vscode"}
    removed_modules = 0
    removed_dirs = 0
    removed_files = 0

    # 1. Project modules ko sys.modules se hatayein (current modules ko skip karein)
    current_mods = {
        "__main__",
        "main",
        "clear_pycache",
        "cleaner",
        "App.src.cleaner",
        "App.src.cleaner.clear_pycache",
        __name__,
    }
    for module_name, module in list(sys.modules.items()):
        if module is None or module_name in current_mods:
            continue
        module_file = getattr(module, "__file__", None)
        if not module_file:
            continue
        try:
            file_path = Path(module_file).resolve()
            if any(x in exclude for x in file_path.parts):
                continue
            if file_path.suffix in {".py", ".pyc", ".pyo"} and project_path in file_path.parents:
                del sys.modules[module_name]
                removed_modules += 1
        except (OSError, ValueError, TypeError):
            continue

    # 2. Sabhi __pycache__ folders aur .pyc files delete karein (os.walk with in-place pruning)
    for root, dirs, files in os.walk(project_path, topdown=True):
        # In-place prune: exclude wale folders ke andar bilkul mat jao
        dirs[:] = [d for d in dirs if d not in exclude and not d.startswith(".")]

        for d in list(dirs):
            if d == "__pycache__":
                pycache_dir = Path(root) / d
                try:
                    shutil.rmtree(pycache_dir, ignore_errors=True)
                    removed_dirs += 1
                except Exception:
                    pass
                dirs.remove(d)

        for f in files:
            if f.endswith((".pyc", ".pyo")):
                pyc_file = Path(root) / f
                try:
                    pyc_file.unlink(missing_ok=True)
                    removed_files += 1
                except Exception:
                    pass

    return {
        "modules": removed_modules,
        "dirs": removed_dirs,
        "files": removed_files,
    }
