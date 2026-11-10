# -*- coding: utf-8 -*-
"""Verify period tree matches Lead's spec exactly."""
import io, json, os, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
d = json.load(io.open(os.path.join(TMP, "world_periods.json"), encoding="utf-8"))
pidx = {x["id"]: x for x in d}

SPEC = {
    "w-prehistory": (-3000000, -3600),
    "w-ancient-near-east": (-3600, -800),
    "w-classical-greece": (-800, -146),
    "w-roman": (-753, 476),
    "w-post-roman": (476, 1000),
    "w-medieval": (1000, 1300),
    "w-renaissance": (1300, 1600),
    "w-early-modern": (1600, 1800),
    "w-modern": (1800, 1914),
    "w-contemporary": (1914, 2026),
}
REGIONAL = {
    "w-ancient-china": (-1600, 1912),
    "w-old-world": (-3000, 1599),
    "w-america-precol": (-2000, 1696),
    "w-ancient-south-asia": (-3000, -185),
}

print("=== spine check ===")
for pid, (s, e) in SPEC.items():
    x = pidx.get(pid)
    if not x:
        print("MISSING", pid); continue
    ok = (x["startYear"], x["endYear"]) == (s, e)
    tagok = "编年主干" in (x.get("tags") or [])
    par = x.get("parentId")
    print("%-22s %8d..%-6d expect %8d..%-6d  range=%s tag=%s parent=%s" %
          (pid, x["startYear"], x["endYear"], s, e, "OK" if ok else "MISMATCH",
           "OK" if tagok else "MISSING", par))
print("=== regional check ===")
for pid, (s, e) in REGIONAL.items():
    x = pidx.get(pid)
    if not x:
        print("MISSING", pid); continue
    ok = (x["startYear"], x["endYear"]) == (s, e)
    tagok = "区域专题" in (x.get("tags") or [])
    print("%-22s %8d..%-6d expect %8d..%-6d  range=%s tag=%s parent=%s" %
          (pid, x["startYear"], x["endYear"], s, e, "OK" if ok else "MISMATCH",
           "OK" if tagok else "MISSING", x.get("parentId")))
roots = [x for x in d if x.get("parentId") is None]
print("roots:", len(roots))
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None: continue
    if p not in pidx:
        print("DANGLING", x["id"], p); bad += 1; continue
    pr = pidx[p]
    if pr["startYear"] > x["startYear"] or x["endYear"] > pr["endYear"]:
        print("RANGE", x["id"], x["startYear"], x["endYear"], "parent", p, pr["startYear"], pr["endYear"]); bad += 1
print("total periods:", len(d), "issues:", bad)
