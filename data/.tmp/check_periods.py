# -*- coding: utf-8 -*-
"""校验 periods 树（Lead 需求版）。"""
import importlib.util
import collections
import sys

spec = importlib.util.spec_from_file_location("p", "periods_data.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = m.PERIODS

errs = []
warns = []

c = collections.Counter(p["id"] for p in P)
for k, v in c.items():
    if v > 1:
        errs.append("DUP id: %s (%d)" % (k, v))

d = {}
for p in P:
    d.setdefault(p["id"], p)

for p in P:
    if p["startYear"] > p["endYear"]:
        errs.append("ORDER %s %d>%d" % (p["id"], p["startYear"], p["endYear"]))
    par = p.get("parentId")
    if par:
        if par not in d:
            errs.append("MISSING PARENT %s -> %s" % (p["id"], par))
        else:
            q = d[par]
            if not (q["startYear"] <= p["startYear"] and p["endYear"] <= q["endYear"]):
                errs.append("RANGE %s [%d,%d] not in %s [%d,%d]" % (
                    p["id"], p["startYear"], p["endYear"], par, q["startYear"], q["endYear"]))
    nk = len(p.get("keyFigures") or [])
    nr = len(p.get("relatedEvents") or [])
    if nk < 3:
        errs.append("KEYFIG <3 %s = %d" % (p["id"], nk))
    if nr < 3:
        errs.append("RELEV <3 %s = %d" % (p["id"], nr))
    for f in ("summary", "territory", "capital", "population", "culture", "tags", "colorKey"):
        if not p.get(f):
            errs.append("MISSING FIELD %s.%s" % (p["id"], f))
    sl = len(p.get("summary", ""))
    if not (150 <= sl <= 400):
        errs.append("SUMMARY LEN %s = %d" % (p["id"], sl))

top = [p for p in P if not p.get("parentId")]
depth = collections.Counter()
for p in P:
    lvl, q = 0, p
    while q.get("parentId"):
        q = d[q["parentId"]]
        lvl += 1
    depth[lvl] += 1

print("period count:", len(P))
print("top level:", len(top))
for p in sorted(top, key=lambda x: x["startYear"]):
    print("   %-22s %-14s %5d..%-5d" % (p["id"], p["name"], p["startYear"], p["endYear"]))
print("depth histogram:", dict(depth))

if errs:
    print("\n=== ERRORS (%d) ===" % len(errs))
    for e in errs:
        print(" ", e)
    sys.exit(1)
print("\nOK")
