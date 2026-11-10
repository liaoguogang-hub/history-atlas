# -*- coding: utf-8 -*-
"""List target figures: bio < 300 OR no relatedEvents. Split by already-done."""
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
print("目标总数:", len(r))
todo = [f for f in r if f["id"] not in done]
print("尚未覆盖:", len(todo))
print("已覆盖:", len(r) - len(todo))
print()
for f in r:
    mark = "已做" if f["id"] in done else "待做"
    p = periods.get(f.get("periodId"), {})
    print("%s %-32s %-13s bio=%4d ach=%d relF=%d | %s / %s" % (
        mark, f["id"], (f.get("name") or "")[:11],
        len(f.get("biography") or ""), len(f.get("achievements") or []),
        len(f.get("relatedFigures") or []),
        p.get("name", "?"), (f.get("role") or "")))
