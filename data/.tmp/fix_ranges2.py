# -*- coding: utf-8 -*-
"""Second pass: re-parent cross-cutting regional nodes + fix remaining ranges."""
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


def par(pid, p):
    idx[pid]["parentId"] = p


# --- widen roots so cross-cutting regional branches fit, keeping roots accurate ---
rng("w-ancient-near-east", -3600, -501); txt("w-ancient-near-east", "公元前3600年", "公元前501年")
rng("w-ancient-china", -1600, 1913); txt("w-ancient-china", "公元前1600年", "公元1913年")
rng("w-classical-greece", -3000, -146); txt("w-classical-greece", "公元前3000年", "公元前146年")
rng("w-post-roman", 476, 1291); txt("w-post-roman", "公元476年", "公元1291年")
rng("w-medieval", 760, 1499); txt("w-medieval", "公元760年", "公元1499年")
rng("w-early-modern", 1492, 1913); txt("w-early-modern", "公元1492年", "公元1913年")
rng("w-modern", 1750, 1945); txt("w-modern", "公元1750年", "公元1945年")

# --- fit children ---
rng("w-sumer", -3500, -2334); txt("w-sumer", "公元前3500年", "公元前2334年")
rng("w-egypt-old", -3100, -332); txt("w-egypt-old", "公元前3100年", "公元前332年")
rng("w-near-east-persian", -550, -330); txt("w-near-east-persian", "公元前550年", "公元前330年")
rng("w-old-world", -3000, 1599); txt("w-old-world", "公元前3000年", "公元1599年")
par("w-old-world", "w-ancient-near-east")

rng("w-america-precol", -2000, 1696); txt("w-america-precol", "公元前2000年", "公元1696年")
par("w-america-precol", "w-classical-greece")

rng("w-east-asia", -500, 1913); txt("w-east-asia", "公元前500年", "公元1913年")
par("w-east-asia", "w-ancient-china")

rng("w-southeast-asia", -200, 1913); txt("w-southeast-asia", "公元前200年", "公元1913年")
par("w-southeast-asia", "w-early-modern")

rng("w-oceania", -1500, 1913); txt("w-oceania", "公元前1500年", "公元1913年")
par("w-oceania", "w-early-modern")

rng("w-abbasid-golden", 750, 1258); txt("w-abbasid-golden", "公元750年", "公元1258年")
par("w-abbasid-golden", "w-post-roman")

rng("w-carolingian", 768, 987); txt("w-carolingian", "公元768年", "公元987年")
par("w-carolingian", "w-post-roman")

rng("w-medieval-china", 960, 1368); txt("w-medieval-china", "公元960年", "公元1368年")
par("w-medieval-china", "w-medieval")

rng("w-crusades", 1095, 1291); txt("w-crusades", "公元1095年", "公元1291年")
par("w-crusades", "w-post-roman")

rng("w-mongol-empire", 1206, 1368); txt("w-mongol-empire", "公元1206年", "公元1368年")
par("w-mongol-empire", "w-medieval")

rng("w-medieval-islam", 1000, 1499); txt("w-medieval-islam", "公元1000年", "公元1499年")
par("w-medieval-islam", "w-medieval")

rng("w-world-wars", 1914, 1945); txt("w-world-wars", "公元1914年", "公元1945年")
par("w-world-wars", "w-modern")

rng("w-ming-qing", 1368, 1911); txt("w-ming-qing", "公元1368年", "公元1911年")
par("w-ming-qing", "w-ancient-china")

rng("w-tang-song", 618, 1279); txt("w-tang-song", "公元618年", "公元1279年")
par("w-tang-song", "w-ancient-china")

rng("w-korea", -500, 1910); txt("w-korea", "公元前500年", "公元1910年")
par("w-korea", "w-east-asia")
rng("w-japan", -500, 1913); txt("w-japan", "公元前500年", "公元1913年")
par("w-japan", "w-east-asia")

rng("w-africa-west", 700, 1599); txt("w-africa-west", "公元700年", "公元1599年")
par("w-africa-west", "w-old-world")
rng("w-africa-east", -300, 1599); txt("w-africa-east", "公元前300年", "公元1599年")
par("w-africa-east", "w-old-world")

rng("w-maya", -200, 1696); txt("w-maya", "公元前200年", "公元1696年")
par("w-maya", "w-america-precol")
rng("w-mesoamerica", 100, 1521); txt("w-mesoamerica", "公元100年", "公元1521年")
par("w-mesoamerica", "w-america-precol")
rng("w-andes", -900, 1533); txt("w-andes", "公元前900年", "公元1533年")
par("w-andes", "w-america-precol")

rng("w-byzantium", 330, 1452); txt("w-byzantium", "公元330年", "公元1452年")
par("w-byzantium", "w-roman")

rng("w-islamic-golden", 762, 1258); txt("w-islamic-golden", "公元762年", "公元1258年")
par("w-islamic-golden", "w-abbasid-golden")

rng("w-hellenistic", -336, -146); txt("w-hellenistic", "公元前336年", "公元前146年")
par("w-hellenistic", "w-classical-greece")
rng("w-macedonian", -336, -301); txt("w-macedonian", "公元前336年", "公元前301年")
par("w-macedonian", "w-hellenistic")

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# validate
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
for r in roots:
    print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
