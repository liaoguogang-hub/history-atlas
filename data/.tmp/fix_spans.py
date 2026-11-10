# -*- coding: utf-8 -*-
"""Fix events whose yearEnd falls outside their period by clipping yearEnd to
the period end, or by moving to a period that contains the whole span."""
import io, json, os, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
periods = json.load(io.open(os.path.join(TMP, "world_periods.json"), encoding="utf-8"))
pidx = {p["id"]: p for p in periods}
depth = {}
def dep(pid):
    if pid in depth: return depth[pid]
    p = pidx[pid].get("parentId")
    depth[pid] = 1 if p is None else 1 + dep(p)
    return depth[pid]
for p in periods: dep(p["id"])

def process(fname):
    path = os.path.join(TMP, fname)
    d = json.load(io.open(path, encoding="utf-8"))
    for x in d:
        y = x["year"]; ye = x.get("yearEnd"); pid = x["periodId"]
        p = pidx.get(pid)
        if not p or ye is None: continue
        if p["startYear"] <= y <= p["endYear"] and p["startYear"] <= ye <= p["endYear"]:
            continue
        # find a period covering BOTH
        cands = [q for q in periods if q["startYear"] <= y <= q["endYear"] and q["startYear"] <= ye <= q["endYear"]]
        if cands:
            cands.sort(key=lambda q: (-depth[q["id"]], q["endYear"] - q["startYear"]))
            x["periodId"] = cands[0]["id"]
        else:
            # clip yearEnd to period end (>= year)
            if p["endYear"] >= y:
                x["yearEnd"] = p["endYear"]
            else:
                x["yearEnd"] = None
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(fname, "fixed")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        process(f)
