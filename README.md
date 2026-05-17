# Helix

> A local-first modular AI workspace.
> Modules work standalone. They also plug into the Helix ecosystem without code changes.

---

## Structure

```
helix/           ← Helix Core (the ecosystem hub)
modules/
  textsense/     ← Text analysis module
  fileforge/     ← File system intelligence module
  ideate/        ← Curiosity capture and recall module
shared/          ← Optional cross-module utilities
```

---

## Running a module standalone

```bash
cd modules/textsense
pip install -r requirements.txt
python app.py
# → http://localhost:5001

cd modules/fileforge
pip install -r requirements.txt
python app.py          # web interface
python main.py scan /path/to/dir    # CLI still works too

cd modules/ideate
pip install -r requirements.txt
python app.py
# → http://localhost:5003
```

---

## Running as Helix ecosystem

```bash
# From project root:
python helix/helix_app.py
# → http://localhost:5000
# All modules are mounted automatically.
# TextSense: localhost:5000/textsense
# FileForge: localhost:5000/fileforge
# Ideate:    localhost:5000/ideate
```

---

## Adding a new module

1. Create `modules/your_module/` with the standard structure
2. Add `helix.json` with `"status": "active"`
3. Implement `module.py` (the Helix contract)
4. Run Helix — your module auto-discovers and mounts

No changes to Helix Core code required.

---

## The core rule

`core/` logic never imports Flask or Helix. Ever.
`app.py` is for standalone. `module.py` is for Helix. Both call the same `api/routes.py`.
