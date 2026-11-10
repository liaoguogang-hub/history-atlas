# -*- coding: utf-8 -*-
"""List events with no figures, grouped by period; list valid period ids."""
import io, json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
pm = {p["id"]: p.get("name") for p in d["periods"]}
nf = [e for e in d["events"] if not e.get("figures")]
c = Counter(e.get("periodId") or "?" for e in nf)
t = Counter(e.get("periodId") or "?" for e in d["events"])
print("无人物事件:", len(nf), "/ 总事件:", len(d["events"]))
print()
for k, v in c.most_common(25):
    print("  %-18s %3d/%3d  %s" % (pm.get(k, "?"), v, t.get(k, 0), k))
print()
print("=== 无人物事件明细（按时期）===")
for k, v in c.most_common(25):
    print("--- %s (%s) ---" % (pm.get(k, "?"), k))
    for e in d["events"]:
        if e.get("periodId") == k and not e.get("figures"):
            print("   %-38s %5s  %s" % (e["id"], e["year"], e["name"]))
