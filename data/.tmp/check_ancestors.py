# -*- coding: utf-8 -*-
"""Check top-level ancestors for the 3 unmatched figures and their target events."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
pmap = {p["id"]: p for p in d["periods"]}


def top(pid):
    node = pmap.get(pid)
    seen = set()
    while node and node.get("parentId") and node["id"] not in seen:
        seen.add(node["id"])
        node = pmap.get(node.get("parentId"))
    return node["id"] if node else None


new = json.load(io.open(os.path.join(TMP, "world_fig_new2.json"), encoding="utf-8"))
for f in new:
    if f["id"] in ("fig-w-muqaddimah-author", "fig-w-ottoman-founder", "fig-w-christian-miracle"):
        t = top(f["periodId"])
        print("%-26s period=%-22s top=%-20s name=%s" % (
            f["id"], f["periodId"], t, pmap.get(t, {}).get("name")))
        for e in d["events"]:
            if e["id"] in ("ev-mu-quran", "ev-isl-rashidun-expansion", "ev-discover-ottoman-empire",
                           "ev-med-euro-viking"):
                print("      event %-34s top=%-20s %s" % (e["id"], top(e["periodId"]),
                                                          pmap.get(top(e["periodId"]), {}).get("name")))
print()
print("=== 各顶层时期 ===")
for p in d["periods"]:
    if p.get("parentId") is None:
        print("   %-24s %s" % (p["id"], p.get("name")))
