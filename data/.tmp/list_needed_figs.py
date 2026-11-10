# -*- coding: utf-8 -*-
"""统计需要哪些 figure id，以及各自被引用次数（用于分级）。"""
import json
import glob
import collections

need = collections.Counter()
where = collections.defaultdict(set)

for f in sorted(glob.glob("evdata_*.json")):
    for e in json.load(open(f, encoding="utf-8")):
        for fid in e.get("f", []):
            need[fid] += 1
            where[fid].add(e["id"])

for f in sorted(glob.glob("china_periods.json")):
    for p in json.load(open(f, encoding="utf-8")):
        for fid in p.get("keyFigures", []):
            need[fid] += 2
            where[fid].add("P:" + p["id"])

# 已写出的人物
have = set()
for f in sorted(glob.glob("figdata_*.json")):
    for p in json.load(open(f, encoding="utf-8")):
        have.add(p["id"])

missing = sorted(need.keys() - have)
print("total referenced:", len(need))
print("already written:", len(have & set(need)))
print("MISSING:", len(missing))
print()
for fid in missing:
    print("%-34s x%-3d %s" % (fid, need[fid], " ".join(sorted(where[fid]))[:110]))

json.dump(sorted(missing), open("missing_figs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
