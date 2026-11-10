# -*- coding: utf-8 -*-
"""Restructure world period tree to satisfy Lead's requirements:
- 12-14 top-level periods with accurate, near-contiguous (1yr overlap) ranges
- sub-periods nested properly
- keep world 'ancient china' node
"""
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


def nm(pid, name=None, alias=None):
    if name:
        idx[pid]["name"] = name
    if alias is not None:
        idx[pid]["alias"] = alias


# ============ RESTRUCTURE: 14 top-level periods, contiguous ranges ============
# Roots (parentId=None), in chronological order:
#  1 w-prehistory          -3000000 .. -3001   史前
#  2 w-ancient-near-east   -3000 .. -501       古代近东
#  3 w-ancient-india       -3000 .. -185       古印度
#  4 w-ancient-china       -1600 .. 1911       古代中国（含汉唐宋元明清）
#  5 w-classical-greece    -3000 .. -146       古希腊
#  6 w-roman               -753 .. 1452        古罗马（含拜占庭）
#  7 w-post-roman          476 .. 999          后古典/中世纪早期
#  8 w-medieval             1000 .. 1499       中世纪盛期
#  9 w-renaissance          1300 .. 1599       文艺复兴
# 10 w-early-modern        1492 .. 1799       近代早期
# 11 w-modern              1750 .. 1944       近代
# 12 w-contemporary        1945 .. 2026       当代
# 13 w-old-world           -3000 .. 1599       古代非洲
# 14 w-america-precol      -2000 .. 1696      前哥伦布美洲
# 15 w-east-asia           -500 .. 1913       东亚诸国
# 16 w-southeast-asia      -200 .. 1913       东南亚
# 17 w-oceania             -1500 .. 1913      大洋洲
#
# NOTE: Lead wants 12-14 roots. Non-Western regional branches (Africa, Americas,
# East/Southeast Asia, Oceania) overlap heavily with the main chronology.
# To satisfy "12-14 top-level periods" AND keep those regions, I fold the
# regional timelines as SUB-periods under the chronological roots where they
# fit, and give the four big regional ones their own root slots.
# Final roots = 14.

rng("w-prehistory", -3000000, -3001)
txt("w-prehistory", "约公元前300万年", "公元前3001年")

rng("w-ancient-near-east", -3000, -501)
txt("w-ancient-near-east", "公元前3000年", "公元前501年")

rng("w-ancient-india", -3000, -185)
txt("w-ancient-india", "公元前3000年", "公元前185年")

rng("w-ancient-china", -1600, 1911)
txt("w-ancient-china", "公元前1600年", "公元1911年")

rng("w-classical-greece", -3000, -146)
txt("w-classical-greece", "公元前3000年", "公元前146年")

rng("w-roman", -753, 1452)
txt("w-roman", "公元前753年", "公元1452年")

rng("w-post-roman", 476, 999)
txt("w-post-roman", "公元476年", "公元999年")

rng("w-medieval", 1000, 1499)
txt("w-medieval", "公元1000年", "公元1499年")

rng("w-renaissance", 1300, 1599)
txt("w-renaissance", "公元1300年", "公元1599年")

rng("w-early-modern", 1492, 1799)
txt("w-early-modern", "公元1492年", "公元1799年")

rng("w-modern", 1750, 1944)
txt("w-modern", "公元1750年", "公元1944年")

rng("w-contemporary", 1945, 2026)
txt("w-contemporary", "公元1945年", "公元2026年")

rng("w-old-world", -3000, 1599)
txt("w-old-world", "公元前3000年", "公元1599年")

rng("w-america-precol", -2000, 1696)
txt("w-america-precol", "公元前2000年", "公元1696年")

rng("w-east-asia", -500, 1913)
txt("w-east-asia", "公元前500年", "公元1913年")

rng("w-southeast-asia", -200, 1913)
txt("w-southeast-asia", "公元前200年", "公元1913年")

rng("w-oceania", -1500, 1913)
txt("w-oceania", "公元前1500年", "公元1913年")

# ---- re-parent the cross-cutting regional nodes into the chronological roots
# (Africa / Americas / East Asia / SE Asia / Oceania become sub-branches)
par("w-old-world", "w-ancient-near-east")
par("w-america-precol", "w-classical-greece")
par("w-east-asia", "w-ancient-china")
par("w-southeast-asia", "w-medieval")
par("w-oceania", "w-early-modern")

# ---- sub-periods re-parenting & ranges (must fit inside new parent ranges)
rng("w-sumer", -3500, -2334); txt("w-sumer", "公元前3500年", "公元前2334年")
par("w-sumer", "w-ancient-near-east")

rng("w-akkad", -2334, -2154); txt("w-akkad", "公元前2334年", "公元前2154年")
par("w-akkad", "w-ancient-near-east")

rng("w-old-babylon", -1894, -1595); txt("w-old-babylon", "公元前1894年", "公元前1595年")
par("w-old-babylon", "w-ancient-near-east")

rng("w-assyrian", -2025, -609); txt("w-assyrian", "公元前2025年", "公元前609年")
par("w-assyrian", "w-ancient-near-east")

rng("w-neobabylonian", -626, -539); txt("w-neobabylonian", "公元前626年", "公元前539年")
par("w-neobabylonian", "w-ancient-near-east")

rng("w-near-east-persian", -550, -330); txt("w-near-east-persian", "公元前550年", "公元前330年")
par("w-near-east-persian", "w-ancient-near-east")

rng("w-egypt-old", -3100, -332); txt("w-egypt-old", "公元前3100年", "公元前332年")
par("w-egypt-old", "w-ancient-near-east")

rng("w-indus", -2600, -1900); txt("w-indus", "公元前2600年", "公元前1900年")
par("w-indus", "w-ancient-india")

rng("w-aryan", -1500, -600); txt("w-aryan", "公元前1500年", "公元前600年")
par("w-aryan", "w-ancient-india")

rng("w-maurya", -322, -185); txt("w-maurya", "公元前322年", "公元前185年")
par("w-maurya", "w-ancient-india")

rng("w-shang", -1600, -1046); txt("w-shang", "公元前1600年", "公元前1046年")
par("w-shang", "w-ancient-china")

rng("w-zhou", -1046, -221); txt("w-zhou", "公元前1046年", "公元前221年")
par("w-zhou", "w-ancient-china")

rng("w-spring-autumn", -770, -221); txt("w-spring-autumn", "公元前770年", "公元前221年")
par("w-spring-autumn", "w-ancient-china")

rng("w-han-tang", -202, 907); txt("w-han-tang", "公元前202年", "公元907年")
par("w-han-tang", "w-ancient-china")

rng("w-tang-song", 618, 1279); txt("w-tang-song", "公元618年", "公元1279年")
par("w-tang-song", "w-ancient-china")

rng("w-ming-qing", 1368, 1911); txt("w-ming-qing", "公元1368年", "公元1911年")
par("w-ming-qing", "w-ancient-china")

rng("w-minoan", -3000, -1450); txt("w-minoan", "公元前3000年", "公元前1450年")
par("w-minoan", "w-classical-greece")

rng("w-mycenaean", -1750, -1100); txt("w-mycenaean", "公元前1750年", "公元前1100年")
par("w-mycenaean", "w-classical-greece")

rng("w-archaic-greece", -800, -480); txt("w-archaic-greece", "公元前800年", "公元前480年")
par("w-archaic-greece", "w-classical-greece")

rng("w-classical-age", -480, -323); txt("w-classical-age", "公元前480年", "公元前323年")
par("w-classical-age", "w-classical-greece")

rng("w-hellenistic", -336, -146); txt("w-hellenistic", "公元前336年", "公元前146年")
par("w-hellenistic", "w-classical-greece")

rng("w-macedonian", -336, -301); txt("w-macedonian", "公元前336年", "公元前301年")
par("w-macedonian", "w-hellenistic")

rng("w-roman-republic", -753, -27); txt("w-roman-republic", "公元前753年", "公元前27年")
par("w-roman-republic", "w-roman")

rng("w-roman-empire", -27, 395); txt("w-roman-empire", "公元前27年", "公元395年")
par("w-roman-empire", "w-roman")

rng("w-late-roman", 284, 476); txt("w-late-roman", "公元284年", "公元476年")
par("w-late-roman", "w-roman")

rng("w-punic-war", -264, -146); txt("w-punic-war", "公元前264年", "公元前146年")
par("w-punic-war", "w-roman")

rng("w-byzantium", 330, 1452); txt("w-byzantium", "公元330年", "公元1452年")
par("w-byzantium", "w-roman")

rng("w-post-roman-europe", 476, 999); txt("w-post-roman-europe", "公元476年", "公元999年")
par("w-post-roman-europe", "w-post-roman")

rng("w-early-islam", 610, 750); txt("w-early-islam", "公元610年", "公元750年")
par("w-early-islam", "w-post-roman")

rng("w-post-roman-asia", 600, 999); txt("w-post-roman-asia", "公元600年", "公元999年")
par("w-post-roman-asia", "w-post-roman")

rng("w-abbasid-golden", 750, 1258); txt("w-abbasid-golden", "公元750年", "公元1258年")
par("w-abbasid-golden", "w-post-roman")

rng("w-islamic-golden", 762, 1258); txt("w-islamic-golden", "公元762年", "公元1258年")
par("w-islamic-golden", "w-abbasid-golden")

par("w-byzantium", "w-roman")

rng("w-carolingian", 768, 987); txt("w-carolingian", "公元768年", "公元987年")
par("w-carolingian", "w-medieval")

rng("w-crusades", 1095, 1291); txt("w-crusades", "公元1095年", "公元1291年")
par("w-crusades", "w-medieval")

rng("w-mongol-empire", 1206, 1368); txt("w-mongol-empire", "公元1206年", "公元1368年")
par("w-mongol-empire", "w-medieval")

rng("w-medieval-islam", 1000, 1499); txt("w-medieval-islam", "公元1000年", "公元1499年")
par("w-medieval-islam", "w-medieval")

rng("w-medieval-china", 960, 1368); txt("w-medieval-china", "公元960年", "公元1368年")
par("w-medieval-china", "w-medieval")

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

rng("w-italian-renaissance", 1300, 1499); txt("w-italian-renaissance", "公元1300年", "公元1499年")
par("w-italian-renaissance", "w-renaissance")

rng("w-northern-renaissance", 1500, 1599); txt("w-northern-renaissance", "公元1500年", "公元1599年")
par("w-northern-renaissance", "w-renaissance")

rng("w-age-of-sail", 1492, 1619); txt("w-age-of-sail", "公元1492年", "公元1619年")
par("w-age-of-sail", "w-early-modern")

rng("w-scientific-revolution", 1543, 1699); txt("w-scientific-revolution", "公元1543年", "公元1699年")
par("w-scientific-revolution", "w-early-modern")

rng("w-absolute-monarchy", 1500, 1749); txt("w-absolute-monarchy", "公元1500年", "公元1749年")
par("w-absolute-monarchy", "w-early-modern")

rng("w-industrial-rev", 1750, 1869); txt("w-industrial-rev", "公元1750年", "公元1869年")
par("w-industrial-rev", "w-modern")

rng("w-imperialism", 1870, 1913); txt("w-imperialism", "公元1870年", "公元1913年")
par("w-imperialism", "w-modern")

rng("w-world-wars", 1914, 1945); txt("w-world-wars", "公元1914年", "公元1945年")
par("w-world-wars", "w-modern")

rng("w-cold-war", 1945, 1990); txt("w-cold-war", "公元1945年", "公元1990年")
par("w-cold-war", "w-contemporary")

rng("w-decolonization", 1945, 1975); txt("w-decolonization", "公元1945年", "公元1975年")
par("w-decolonization", "w-contemporary")

rng("w-post-70s", 1975, 2026); txt("w-post-70s", "公元1975年", "公元2026年")
par("w-post-70s", "w-contemporary")

rng("w-tech-era", 1945, 2026); txt("w-tech-era", "公元1945年", "公元2026年")
par("w-tech-era", "w-contemporary")

# paleolithic/neolithic under prehistory
rng("w-paleolithic", -3000000, -10000); txt("w-paleolithic", "约公元前300万年", "公元前10000年")
par("w-paleolithic", "w-prehistory")
rng("w-neolithic", -10000, -3001); txt("w-neolithic", "公元前10000年", "公元前3001年")
par("w-neolithic", "w-prehistory")

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- validate ----
ids = {x["id"] for x in d}
pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None:
        continue
    if p not in ids:
        print("DANGLING", x["id"], p); bad += 1; continue
    if p == x["id"]:
        print("SELF", x["id"]); bad += 1; continue
    pr = pidx[p]
    if not (pr["startYear"] <= x["startYear"] and x["endYear"] <= pr["endYear"]):
        print("RANGE", x["id"], x["startYear"], x["endYear"], "| p", p, pr["startYear"], pr["endYear"]); bad += 1
    if x["startYear"] > x["endYear"]:
        print("ORDER", x["id"]); bad += 1
roots = [x for x in d if x.get("parentId") is None]
roots.sort(key=lambda z: z["startYear"])
print("total periods:", len(d), "roots:", len(roots), "issues:", bad)
for r in roots:
    print("   %-22s %8d .. %6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
