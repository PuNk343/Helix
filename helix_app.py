"""
helix_app.py — Helix Core entry point.

Run with: python helix/helix_app.py  (from project root)
Opens the Helix dashboard at http://localhost:5000

Discovers all modules in the modules/ directory.
Mounts their Flask blueprints. Serves the unified dashboard.
"""
import atexit
from pathlib import Path
from flask import Flask, jsonify, render_template
from registry import ModuleRegistry

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).parent.parent
MODULES_DIR = ROOT_DIR / "modules"


def create_helix_app():
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )

    # ── Module discovery ───────────────────────────────────────────────────────
    registry = ModuleRegistry(MODULES_DIR)

    print("\n  Helix — starting module discovery...")
    registry.discover()
    print(f"  {len(registry.modules)} module(s) loaded.\n")

    for bp in registry.get_blueprints():
        app.register_blueprint(bp)

    atexit.register(registry.shutdown_all)

    # ── Helix Core routes ──────────────────────────────────────────────────────

    @app.route("/")
    def dashboard():
        modules = registry.list_modules()
        return render_template("dashboard.html", modules=modules)

    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "helix": "0.1.0",
            "modules": registry.health_report(),
        })

    @app.route("/modules")
    def modules():
        return jsonify(registry.list_modules())

    return app


if __name__ == "__main__":
    print("\n  ╔══════════════════════════╗")
    print("  ║   Helix v0.1.0           ║")
    print("  ║   localhost:5000         ║")
    print("  ╚══════════════════════════╝")
    app = create_helix_app()
    app.run(debug=True, port=5000)
