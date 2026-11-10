# -*- coding: utf-8 -*-
"""Rewrite new-figure specs so relatedFigures/relatedEvents only cite ids that
already exist in data/world.json (per Lead's requirement)."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SRC_DIR = os.path.join(TMP, "new_specs")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"

_world = json.load(io.open(W, encoding="utf-8"))
FIG_IDS = {f["id"] for f in _world["figures"]}
EVT_IDS = {e["id"] for e in _world["events"]}

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        rf = [r for r in (e.get("relatedFigures") or []) if r in FIG_IDS]
        re_ = [r for r in (e.get("relatedEvents") or []) if r in EVT_IDS]
        if rf != (e.get("relatedFigures") or []):
            e["relatedFigures"] = rf; changed = True
        if re_ != (e.get("relatedEvents") or []):
            e["relatedEvents"] = re_; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "refs stripped")
