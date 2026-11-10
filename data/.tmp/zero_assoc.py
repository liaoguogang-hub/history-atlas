# -*- coding: utf-8 -*-
"""List world.json figures with no relatedEvents and relatedFigures <= 1."""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
periods = {p["id"]: p for p in d["periods"]}

# figures already covered by expand1
import os
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
done = set()
for fn in os.listdir(os.path.join(TMP, "exp_specs")):
    try:
        for f in json.load(io.open(os.path.join(TMP, "exp_specs", fn), encoding="utf-8")):
            done.add(f["id"])
    except Exception:
        pass

r = [f for f in d["figures"]
     if not f.get("relatedEvents") and len(f.get("relatedFigures") or []) <= 1]
print("零关联人物总数:", len(r))
todo = [f for f in r if f["id"] not in done]
print("其中尚未覆盖:", len(todo))
print("已完成覆盖:", len(r) - len(todo))
print()
for f in r:
    mark = "已做" if f["id"] in done else "待做"
    p = periods.get(f.get("periodId"), {})
    print("%s %-32s %-12s bio=%4d ach=%d | %s / %s" % (
        mark, f["id"], (f.get("name") or "")[:11],
        len(f.get("biography") or ""), len(f.get("achievements") or []),
        p.get("name", "?"), (f.get("role") or "")))
