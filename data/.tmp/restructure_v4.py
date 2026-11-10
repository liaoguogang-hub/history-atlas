# -*- coding: utf-8 -*-
"""Final: clip sub-periods into parents, fix spine ordering."""
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


# Assyria (-2025..-609) and Neo-Babylonian (-626..-539) -> clip to Near East span
setp("w-assyrian", -2025, -801, "w-ancient-near-east")
setp("w-neobabylonian", -800, -539, "w-ancient-near-east")
# Egypt (-3100..-332): clip to classical-greece span (-800..-146) -> -800..-332
setp("w-egypt-old", -800, -332, "w-classical-greece")
# Achaemenid Persia (-550..-330) fits classical-greece already
# Minoan / Mycenaean -> clip into prehistory (-3000000..-3600)
setp("w-minoan", -3600, -1450, "w-prehistory")
setp("w-mycenaean", -3600, -1100, "w-prehistory")

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None:
        continue
    if p not in pidx:
        print("DANGLING", x["id"], p); bad += 1; continue
    pr = pidx[p]
    if pr["startYear"] > x["startYear"] or x["endYear"] > pr["endYear"]:
        print("RANGE", x["id"], x["startYear"], x["endYear"], "| p", p, pr["startYear"], pr["endYear"]); bad += 1
roots = [x for x in d if x.get("parentId") is None]
spine = sorted([r for r in roots if "编年主干" in (r.get("tags") or [])], key=lambda z: z["startYear"])
regional = sorted([r for r in roots if "区域专题" in (r.get("tags") or [])], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
print("SPINE:")
for a, b in zip(spine, spine[1:]):
    flag = "" if b["startYear"] == a["endYear"] else "  <<< GAP/OVERLAP"
    print("   %-20s %8d..%6d  ->  %-20s %8d%s" % (a["id"], a["startYear"], a["endYear"], b["id"], b["startYear"], flag))
print("REGIONAL:")
for r in regional:
    print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
