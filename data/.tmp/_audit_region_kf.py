# -*- coding: utf-8 -*-
"""审视所有地区/专题时期的 keyFigures，找出跨地区的不相干人物。"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

w = json.load(io.open("data/world.json", encoding="utf-8"))
fg = {f["id"]: f for f in w["figures"]}

REGION = [
    "w-southeast-asia", "w-modern-southeast-asia", "w-medieval-southeast-asia",
    "w-ancient-south-asia", "w-medieval-south-asia", "w-modern-south-asia",
    "w-mughal", "w-africa-west", "w-africa-east", "w-modern-africa", "w-old-world",
    "w-maya", "w-mesoamerica", "w-andes", "w-america-precol", "w-latin-america",
    "w-korea", "w-japan", "w-east-asia", "w-oceania", "w-near-east-persian",
]

print("世界史: %d 时期 / %d 事件 / %d 人物" % (
    len(w["periods"]), len(w["events"]), len(w["figures"])))
print()

for pid in REGION:
    p = next((x for x in w["periods"] if x["id"] == pid), None)
    if not p:
        continue
    kf = p.get("keyFigures") or []
    span = "(%s,%s)" % (p.get("startYear"), p.get("endYear"))
    print("%-28s %s" % (pid, span))
    for fid in kf:
        f = fg.get(fid)
        if not f:
            print("    ? %s (不存在)" % fid)
            continue
        role = (f.get("role") or "")[:28]
        print("    %-18s %s~%s  %s" % (f["name"], f.get("birthYear"), f.get("deathYear"), role))
    print()
