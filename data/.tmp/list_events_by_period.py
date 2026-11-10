# -*- coding: utf-8 -*-
"""Print exact event names for periods relevant to the new figures."""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
pm = {p["id"]: p.get("name") for p in d["periods"]}

WANT = ["w-early-islam", "w-post-roman-europe", "w-medieval", "w-crusades",
        "w-medieval-islam", "w-egypt-old", "w-punic-war", "w-japan",
        "w-roman-empire", "w-scientific-revolution", "w-carolingian"]
for pid in WANT:
    print("--- %s (%s) ---" % (pm.get(pid, "?"), pid))
    for e in d["events"]:
        if e.get("periodId") == pid:
            print("   %-44s %s" % (e["name"], e["id"]))
