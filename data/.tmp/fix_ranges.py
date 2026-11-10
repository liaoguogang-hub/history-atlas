# -*- coding: utf-8 -*-
"""Restructure period tree so child ranges fall inside parents."""
import io, json, os

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_periods.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

def rng(pid, s, e):
    idx[pid]["startYear"] = s
    idx[pid]["endYear"] = e

def txt(pid, s, e):
    idx[pid]["startDateText"] = s
    idx[pid]["endDateText"] = e

def dt(y):
    return ("公元前%d年" % (-y)) if y < 0 else ("公元%d年" % y)

def par(pid, p):
    idx[pid]["parentId"] = p

# --- widen parent ranges so children fit ---
rng("w-ancient-near-east", -3500, -300); txt("w-ancient-near-east", "公元前3500年", "公元前300年")
rng("w-ancient-india", -3000, -185); txt("w-ancient-india", "公元前3000年", "公元前185年")
rng("w-ancient-china", -1600, 1912); txt("w-ancient-china", "公元前1600年", "公元1912年")
rng("w-classical-greece", -3000, -146); txt("w-classical-greece", "公元前3000年", "公元前146年")
rng("w-hellenistic", -336, -146); txt("w-hellenistic", "公元前336年", "公元前146年")
rng("w-post-roman", 476, 1458); txt("w-post-roman", "公元476年", "公元1458年")
rng("w-medieval", 330, 1500); txt("w-medieval", "公元330年", "公元1500年")
rng("w-post-roman", 476, 1000); txt("w-post-roman", "公元476年", "公元1000年")
rng("w-early-modern", 1492, 1800); txt("w-early-modern", "公元1492年", "公元1800年")
rng("w-modern", 1750, 1945); txt("w-modern", "公元1750年", "公元1945年")
rng("w-contemporary", 1914, 2026); txt("w-contemporary", "公元1914年", "公元2026年")
rng("w-old-world", -3000, 1600); txt("w-old-world", "公元前3000年", "公元1600年")
rng("w-america-precol", -2000, 1697); txt("w-america-precol", "公元前2000年", "公元1697年")
rng("w-east-asia", -500, 1914); txt("w-east-asia", "公元前500年", "公元1914年")
rng("w-southeast-asia", -200, 1914); txt("w-southeast-asia", "公元前200年", "公元1914年")
rng("w-oceania", -1500, 1914); txt("w-oceania", "公元前1500年", "公元1914年")
rng("w-abbasid-golden", 750, 1258); txt("w-abbasid-golden", "公元750年", "公元1258年")
rng("w-roman", -753, 1453); txt("w-roman", "公元前753年", "公元1453年")
rng("w-prehistory", -3000000, -221); txt("w-prehistory", "约公元前300万年", "公元前221年")

# re-parent things so hierarchy is sensible
par("w-byzantium", "w-medieval")
par("w-abbasid-golden", "w-medieval")
par("w-islamic-golden", "w-abbasid-golden")
par("w-ming-qing", "w-ancient-china")

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# re-check
ids = {x["id"] for x in d}
pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None:
        continue
    if p not in ids:
        print("DANGLING parent", x["id"], p); bad += 1; continue
    if p == x["id"]:
        print("SELF parent", x["id"]); bad += 1; continue
    par_ = pidx[p]
    if not (par_["startYear"] <= x["startYear"] and x["endYear"] <= par_["endYear"]):
        print("RANGE VIOLATION", x["id"], x["startYear"], x["endYear"], "| parent", p, par_["startYear"], par_["endYear"]); bad += 1
    if x["startYear"] > x["endYear"]:
        print("BAD ORDER", x["id"]); bad += 1
print("periods:", len(d), "issues:", bad)

# depth report
def depth(x, seen=None):
    if seen is None: seen = set()
    p = x.get("parentId")
    if p is None: return 1
    if p in seen: return 99
    seen.add(x["id"])
    return 1 + depth(pidx[p], seen)
mx = max(depth(x) for x in d)
print("max depth:", mx)
roots = [x["id"] for x in d if x.get("parentId") is None]
print("roots:", roots)
