# -*- coding: utf-8 -*-
"""Final fixes: satisfy range containment + mark root types for the App's
'对照/同期' matching (chronological spine vs regional topic branch)."""
import io, json, os

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_periods.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}


def rng(pid, s, e):
    idx[pid]["startYear"] = s
    idx[pid]["endYear"] = e


def dt(y):
    return ("公元前%d年" % (-y)) if y < 0 else ("公元%d年" % y)


def txt(pid, s, e):
    idx[pid]["startDateText"] = s
    idx[pid]["endDateText"] = e


# extend Near East root to cover Ptolemaic Egypt & Achaemenid Persia tail
rng("w-ancient-near-east", -3600, -330)
txt("w-ancient-near-east", dt(-3600), dt(-330))
rng("w-egypt-old", -3600, -332); txt("w-egypt-old", dt(-3600), dt(-332))
rng("w-near-east-persian", -550, -330); txt("w-near-east-persian", dt(-550), dt(-330))

# regional branch roots need ranges that don't clash with the chronological spine
# -> clip them to a plausible span and tag them as regional topics
rng("w-old-world", -3000, 1599); txt("w-old-world", dt(-3000), dt(1599))
rng("w-america-precol", -2000, 1696); txt("w-america-precol", dt(-2000), dt(1696))
rng("w-east-asia", -500, 1913); txt("w-east-asia", dt(-500), dt(1913))
rng("w-southeast-asia", 1492, 1913); txt("w-southeast-asia", dt(1492), dt(1913))
rng("w-oceania", 1492, 1913); txt("w-oceania", dt(1492), dt(1913))

# mark root character for App matching
CHRONO = {
    "w-prehistory", "w-ancient-near-east", "w-ancient-india", "w-classical-greece",
    "w-ancient-china", "w-roman", "w-post-roman", "w-medieval", "w-renaissance",
    "w-early-modern", "w-modern", "w-contemporary",
}
for x in d:
    if x.get("parentId") is None:
        if x["id"] in CHRONO:
            x["tags"] = list(dict.fromkeys((x.get("tags") or []) + ["编年主干"]))
        else:
            x["tags"] = list(dict.fromkeys((x.get("tags") or []) + ["区域专题"]))

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ids = {x["id"] for x in d}
pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None:
        continue
    if p not in ids:
        print("DANGLING", x["id"], p); bad += 1; continue
    pr = pidx[p]
    if not (pr["startYear"] <= x["startYear"] and x["endYear"] <= pr["endYear"]):
        print("RANGE", x["id"], x["startYear"], x["endYear"], "| p", p, pr["startYear"], pr["endYear"]); bad += 1
roots = sorted([x for x in d if x.get("parentId") is None], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
