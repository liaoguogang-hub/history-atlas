# -*- coding: utf-8 -*-
"""Clip Near East / Greek children so all fit their parents."""
import io, json, os

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_periods.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}


def dt(y):
    return ("公元前%d年" % (-y)) if y < 0 else ("公元%d年" % y)


def setp(pid, s, e, parent=None):
    x = idx[pid]
    x["startYear"] = s
    x["endYear"] = e
    x["startDateText"] = dt(s)
    x["endDateText"] = dt(e)
    if parent is not None:
        x["parentId"] = parent
    return x


# Assyria (-2025..-609) ends after parent (-800) -> clip to -801
setp("w-assyrian", -2025, -801, "w-ancient-near-east")
# Egypt (-3600..-332) -> clip into near-east span
setp("w-egypt-old", -3600, -801, "w-ancient-near-east")
# Achaemenid Persia (-550..-330) -> move under classical-greece? no: it belongs with
# the Hellenistic age. Give it to w-classical-greece (-800..-146) which contains it.
setp("w-near-east-persian", -550, -330, "w-classical-greece")

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None: continue
    if p not in pidx:
        print("DANGLING", x["id"], p); bad += 1; continue
    pr = pidx[p]
    if pr["startYear"] > x["startYear"] or x["endYear"] > pr["endYear"]:
        print("RANGE", x["id"], x["startYear"], x["endYear"], "| p", p, pr["startYear"], pr["endYear"]); bad += 1
roots = [x for x in d if x.get("parentId") is None]
print("total:", len(d), "roots:", len(roots), "issues:", bad)
