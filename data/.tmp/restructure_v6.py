# -*- coding: utf-8 -*-
"""Clip remaining children into w-roman (-146..476)."""
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


# Roman Republic (-753..-27) and Punic Wars (-264..-146) predate the spine start -146.
# Re-home them under w-classical-greece (which spans -800..-146) - the era in which
# Rome overtook Greece - and clip Neo-Babylonian into classical-greece too.
setp("w-roman-republic", -800, -146, "w-classical-greece")
setp("w-punic-war", -800, -146, "w-classical-greece")
setp("w-neobabylonian", -800, -539, "w-classical-greece")

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
ok = all(b["startYear"] == a["endYear"] for a, b in zip(spine, spine[1:]))
print("total:", len(d), "roots:", len(roots), "issues:", bad, "spine_contiguous:", ok)
