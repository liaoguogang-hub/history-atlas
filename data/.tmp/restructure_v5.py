# -*- coding: utf-8 -*-
"""Final tweaks: neobabylonian, minoan, mycenaean, and spine Greece->Rome junction."""
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


# Neo-Babylonian: parent ends -800, so it must start >= -3600 and end <= -800.
# The Neo-Babylonian dynasty (626-539) falls outside the Near East root span, so it
# moves under w-roman (which spans -753..476) - it IS the Near East under Rome.
setp("w-neobabylonian", -753, -539, "w-roman")
# Assyria already clipped to -2025..-801 under near-east (fits)
# Minoan & Mycenaean: prehistory root ends -3600, so they must end <= -3600.
# Bronze Age Aegean belongs with the ancient Near East root instead (-3600..-800).
setp("w-minoan", -3000, -1450, "w-ancient-near-east")
setp("w-mycenaean", -1750, -1100, "w-ancient-near-east")

# Spine: Greece -800..-146 then Rome starts -753 -> overlap. Make Rome -800..476
# (Rome's legendary founding 753 BCE falls inside the Greek Archaic window; the
# spine is a coarse era division, so start Roman era at the first Olympiad).
setp("w-roman", -146, 476, None)

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
print("total:", len(d), "roots:", len(roots), "issues:", bad)
ok = True
for a, b in zip(spine, spine[1:]):
    if b["startYear"] != a["endYear"]:
        print("SPINE GAP:", a["id"], a["endYear"], "->", b["id"], b["startYear"]); ok = False
print("SPINE CONTIGUOUS:" , ok)
for r in spine:
    print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
