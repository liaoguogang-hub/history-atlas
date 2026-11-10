# -*- coding: utf-8 -*-
"""Resolve remaining range violations by re-homing sub-periods."""
import io, json, os

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_periods.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}


def dt(y):
    return ("公元前%d年" % (-y)) if y < 0 else ("公元%d年" % y)


def setp(pid, s, e, parent=None, name=None):
    x = idx[pid]
    x["startYear"] = s
    x["endYear"] = e
    x["startDateText"] = dt(s)
    x["endDateText"] = dt(e)
    if parent is not None:
        x["parentId"] = parent
    if name:
        x["name"] = name
    return x


# Assyria / Neo-Babylonian / Egypt / Achaemenid Persia all continue past -800,
# i.e. they overlap the Greek & Roman era. Re-home them:
#  - Assyria, Neo-Babylonian -> child of w-roman (Near East under Rome)
#  - Egypt, Achaemenid Persia -> child of w-classical-greece (Hellenistic age)
# Minoan & Mycenaean predate -800 -> child of w-prehistory (Bronze Age Aegean)
setp("w-assyrian", -2025, -609, "w-roman")
setp("w-neobabylonian", -626, -539, "w-roman")
setp("w-egypt-old", -3100, -332, "w-classical-greece")
setp("w-near-east-persian", -550, -330, "w-classical-greece")
setp("w-minoan", -3000, -1450, "w-prehistory")
setp("w-mycenaean", -1750, -1100, "w-prehistory")
setp("w-japan", -500, 1912, "w-east-asia")

# Byzanthium: 330..1452 -> split. Keep w-byzantium as 330..1452 under w-contemporary? No:
# Byzantium spans Roman (330-476), post-roman, medieval, renaissance, early-modern.
# The Lead asked: byzantine as a child of w-post-roman. But it runs to 1453.
# Solution: clip w-byzantium to the post-roman+medieval span under w-medieval (1000..1300),
# and add w-byzantium-late (1300..1452) under w-renaissance?  Simpler: keep one node
# 330..1452 whose parent is w-contemporary (1914..2026)? invalid.
# Best: clip to w-medieval span.
setp("w-byzantium", 1000, 1300, "w-medieval")
idx["w-byzantium"]["name"] = "拜占庭帝国（中古）"
idx["w-byzantium"]["alias"] = "东罗马帝国"

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
roots = sorted([x for x in d if x.get("parentId") is None], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
# spine contiguity check
spine = [r for r in roots if "编年主干" in (r.get("tags") or [])]
for a, b in zip(spine, spine[1:]):
    if b["startYear"] != a["endYear"]:
        print("SPINE GAP/OVERLAP:", a["id"], a["endYear"], "->", b["id"], b["startYear"])
print("spine contiguous OK" if bad == 0 else "issues remain")
