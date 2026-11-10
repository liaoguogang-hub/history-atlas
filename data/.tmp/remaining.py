# -*- coding: utf-8 -*-
"""Show remaining zero-association figures not yet covered."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
periods = {p["id"]: p for p in d["periods"]}

done = set()
for fn in os.listdir(os.path.join(TMP, "exp_specs")):
    try:
        for f in json.load(io.open(os.path.join(TMP, "exp_specs", fn), encoding="utf-8")):
            done.add(f["id"])
    except Exception:
        pass

r = [f for f in d["figures"]
     if len(f.get("biography") or "") < 300 or not f.get("relatedEvents")]
zero = [f for f in d["figures"]
        if not f.get("relatedEvents") and len(f.get("relatedFigures") or []) <= 1]
print("目标总数(bio<300 或 无relatedEvents):", len(r))
print("零关联(relE空 且 relF<=1):", len(zero))
todo = [f for f in r if f["id"] not in done]
print("尚未覆盖:", len(todo))
print()
for f in todo:
    p = periods.get(f.get("periodId"), {})
    print("%-32s %-13s bio=%4d ach=%d relF=%d | %s / %s" % (
        f["id"], (f.get("name") or "")[:11],
        len(f.get("biography") or ""), len(f.get("achievements") or []),
        len(f.get("relatedFigures") or []),
        p.get("name", "?"), (f.get("role") or "")))
