# -*- coding: utf-8 -*-
"""Validate event part files: parse, categories, importance, year-in-period, detail length."""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
periods = json.load(io.open(os.path.join(TMP, "world_periods.json"), encoding="utf-8"))
pidx = {p["id"]: p for p in periods}

VALID_CATS = {
    "political", "military", "economic", "cultural", "scientific", "social",
    "religious", "art", "literature", "education", "technology", "exploration",
    "conflict", "treaty", "reform", "dynasty", "cross-civilization", "disaster",
    "health", "economy-crisis",
}

files = [f for f in sys.argv[1:] if f]
allx = []
for f in files:
    path = os.path.join(TMP, f)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print("PARSE FAIL", f, e)
        continue
    print(f, "->", len(d))
    allx.extend(d)

seen = set()
for x in allx:
    eid = x.get("id")
    if eid in seen:
        print("DUP:", eid)
    seen.add(eid)
    for k in ("id", "name", "year", "periodId", "category", "summary", "detail"):
        if k not in x:
            print("MISSING", k, eid)
    if x.get("category") not in VALID_CATS:
        print("BAD CAT", eid, x.get("category"))
    imp = x.get("importance")
    if imp not in (1, 2, 3, 4, 5):
        print("BAD IMPORTANCE", eid, imp)
    pid = x.get("periodId")
    if pid not in pidx:
        print("BAD periodId", eid, pid)
    else:
        p = pidx[pid]
        y = x.get("year")
        ye = x.get("yearEnd")
        if y is not None and not (p["startYear"] <= y <= p["endYear"]):
            print("YEAR OUT OF RANGE", eid, y, "period", pid, p["startYear"], p["endYear"])
        if ye is not None:
            if ye < y:
                print("yearEnd<year", eid)
            if not (p["startYear"] <= ye <= p["endYear"]):
                print("yearEnd OUT OF RANGE", eid, ye, "period", pid)
    d = x.get("detail") or ""
    if not (150 <= len(d) <= 500):
        print("detail len", len(d), eid)
    s = x.get("summary") or ""
    if not (40 <= len(s) <= 120):
        print("summary len", len(s), eid)
    if x.get("year") == 0:
        print("YEAR 0", eid)

print("total events:", len(allx), "unique:", len(seen))
xc = [x for x in allx if x.get("category") == "cross-civilization"]
print("cross-civilization:", len(xc))
no_tags = [x["id"] for x in xc if not (x.get("tags") or [])]
print("xc without tags:", no_tags)
