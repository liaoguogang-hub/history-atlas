# -*- coding: utf-8 -*-
"""Reassign periodIds so build_relations can link the new figures to events."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC_DIR = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs"

REASSIGN = {
    "fig-w-muqaddimah-author": "w-early-islam",
    "fig-w-ottoman-founder": "w-medieval-islam",
    "fig-w-christian-miracle": "w-post-roman-europe",
}

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        if e["id"] in REASSIGN and e["periodId"] != REASSIGN[e["id"]]:
            e["periodId"] = REASSIGN[e["id"]]
            changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "periods reassigned")
