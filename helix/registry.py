"""
registry.py — Module discovery and registration for Helix Core.

Scans the modules/ directory. Finds anything with helix.json + module.py.
Imports module.py, calls initialize(), registers blueprints.

This is intentionally simple. When you're ready, you can add:
  - Hot reload (detect new modules while running)
  - Module health monitoring
  - Dependency resolution (module A requires module B)
"""
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any


class ModuleRegistry:
    def __init__(self, modules_dir: Path):
        self.modules_dir = modules_dir
        self.modules: Dict[str, Any] = {}      # id → imported module object
        self.metadata: Dict[str, dict] = {}    # id → helix.json dict

    def discover(self) -> None:
        """
        Scan modules_dir for valid modules and load them.
        A valid module has both helix.json and module.py.
        Skips modules with status != "active".
        """
        if not self.modules_dir.exists():
            print(f"  [Registry] Modules dir not found: {self.modules_dir}")
            return

        for folder in sorted(self.modules_dir.iterdir()):
            if not folder.is_dir():
                continue

            helix_json = folder / "helix.json"
            module_py  = folder / "module.py"

            if not helix_json.exists() or not module_py.exists():
                continue

            try:
                meta = json.loads(helix_json.read_text())
            except Exception as e:
                print(f"  [Registry] Bad helix.json in {folder.name}: {e}")
                continue

            if meta.get("status") != "active":
                print(f"  [Registry] Skipping {folder.name} (status: {meta.get('status')})")
                continue

            module_id = meta.get("id", folder.name)

            try:
                mod = self._import_module(module_py, module_id)
                success = mod.initialize()
                if success:
                    self.modules[module_id] = mod
                    self.metadata[module_id] = meta
                    print(f"  ✓  {meta.get('name', module_id)} loaded")
                else:
                    print(f"  ✗  {meta.get('name', module_id)} initialize() returned False")
            except Exception as e:
                print(f"  ✗  Failed to load {folder.name}: {e}")

    def _import_module(self, path: Path, name: str):
        """Dynamically import a module.py file."""
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def get_blueprints(self) -> list:
        """Return all blueprints for Helix's Flask app to mount."""
        blueprints = []
        for mod_id, mod in self.modules.items():
            try:
                bp = mod.get_blueprint()
                blueprints.append(bp)
            except Exception as e:
                print(f"  ✗  Blueprint error for {mod_id}: {e}")
        return blueprints

    def health_report(self) -> dict:
        """Return health status of all loaded modules."""
        return {
            mod_id: mod.health_check()
            for mod_id, mod in self.modules.items()
        }

    def list_modules(self) -> list:
        """Return metadata for all loaded modules (for the dashboard)."""
        return [mod.describe() for mod in self.modules.values()]

    def shutdown_all(self) -> None:
        """Call shutdown() on all modules. Use on exit."""
        for mod_id, mod in self.modules.items():
            try:
                mod.shutdown()
            except Exception as e:
                print(f"  [Registry] Shutdown error for {mod_id}: {e}")
