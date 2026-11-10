# -*- coding: utf-8 -*-
"""List figures in data/world.json needing expansion, prioritising sparse links."""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
figs = d["figures"]
periods = {p["id"]: p for p in d["periods"]}

need = []
for f in figs:
    bio = len(f.get("biography") or "")
    ach = len(f.get("achievements") or [])
    relF = len(f.get("relatedFigures") or [])
    relE = len(f.get("relatedEvents") or [])
    if bio < 380 or ach < 6:
        need.append((bio, ach, relF, relE, f))

need.sort(key=lambda t: (t[3] + t[2], t[0]))
print("total figures:", len(figs), " need expansion:", len(need))
print()
for bio, ach, relF, relE, f in need:
    p = periods.get(f.get("periodId"), {})
    print("%-34s %-14s bio=%4d ach=%d relF=%d relE=%d  %s / %s" % (
        f["id"], f.get("name", "")[:12], bio, ach, relF, relE,
        p.get("name", "?"), f.get("role", "")))
