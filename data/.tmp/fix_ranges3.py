# -*- coding: utf-8 -*-
"""Final period tree restructure.

Design: 14 top-level periods, each with an accurate near-contiguous range
(adjacent roots share at most a 1-year boundary). Cross-cutting regional
timelines (Africa / Americas / East Asia / SE Asia / Oceania) are folded as
sub-periods of the chronological root whose span they actually cover, and
their own ranges are clipped to fit.
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


# ---- ROOT definitions: (id, start, end) ----
ROOTS = [
    ("w-prehistory",        -3000000, -3001),   # 史前
    ("w-ancient-near-east", -3600,   -501),     # 古代近东
    ("w-ancient-india",     -3000,   -185),     # 古印度
    ("w-classical-greece",  -3000,   -146),     # 古希腊
    ("w-ancient-china",     -1600,   1913),     # 古代中国
    ("w-roman",             -753,    1452),     # 古罗马
    ("w-post-roman",         476,    1291),     # 后古典/中世纪早期
    ("w-medieval",           760,    1499),     # 中世纪盛期
    ("w-renaissance",       1300,    1599),     # 文艺复兴
    ("w-early-modern",      1492,    1913),     # 近代早期
    ("w-modern",            1750,    1945),     # 近代
    ("w-contemporary",       1945,    2026),     # 当代
    ("w-old-world",         -3000,    1599),     # 古代非洲  (root)
    ("w-america-precol",    -2000,    1696),     # 前哥伦布美洲 (root)
]
for pid, s, e in ROOTS:
    rng(pid, s, e)
    txt(pid, dt(s), dt(e))
    par(pid, None)

# East Asia / SE Asia / Oceania: keep as roots too would exceed 14,
# so they become sub-branches clipped to their host root's span.
par("w-east-asia", "w-ancient-china")
rng("w-east-asia", -500, 1913); txt("w-east-asia", dt(-500), dt(1913))
par("w-southeast-asia", "w-early-modern")
rng("w-southeast-asia", 1492, 1913); txt("w-southeast-asia", dt(1492), dt(1913))
par("w-oceania", "w-early-modern")
rng("w-oceania", 1492, 1913); txt("w-oceania", dt(1492), dt(1913))

# ---- fix remaining children to fit their (possibly changed) parents ----
rng("w-sumer", -3500, -2334); txt("w-sumer", dt(-3500), dt(-2334))
par("w-sumer", "w-ancient-near-east")
rng("w-akkad", -2334, -2154); txt("w-akkad", dt(-2334), dt(-2154))
par("w-akkad", "w-ancient-near-east")
rng("w-old-babylon", -1894, -1595); txt("w-old-babylon", dt(-1894), dt(-1595))
par("w-old-babylon", "w-ancient-near-east")
rng("w-assyrian", -2025, -609); txt("w-assyrian", dt(-2025), dt(-609))
par("w-assyrian", "w-ancient-near-east")
rng("w-neobabylonian", -626, -539); txt("w-neobabylonian", dt(-626), dt(-539))
par("w-neobabylonian", "w-ancient-near-east")
rng("w-egypt-old", -3600, -332); txt("w-egypt-old", dt(-3600), dt(-332))
par("w-egypt-old", "w-ancient-near-east")
rng("w-near-east-persian", -550, -330); txt("w-near-east-persian", dt(-550), dt(-330))
par("w-near-east-persian", "w-ancient-near-east")

rng("w-indus", -2600, -1900); txt("w-indus", dt(-2600), dt(-1900))
par("w-indus", "w-ancient-india")
rng("w-aryan", -1500, -600); txt("w-aryan", dt(-1500), dt(-600))
par("w-aryan", "w-ancient-india")
rng("w-maurya", -322, -185); txt("w-maurya", dt(-322), dt(-185))
par("w-maurya", "w-ancient-india")

rng("w-minoan", -3000, -1450); txt("w-minoan", dt(-3000), dt(-1450))
par("w-minoan", "w-classical-greece")
rng("w-mycenaean", -1750, -1100); txt("w-mycenaean", dt(-1750), dt(-1100))
par("w-mycenaean", "w-classical-greece")
rng("w-archaic-greece", -800, -480); txt("w-archaic-greece", dt(-800), dt(-480))
par("w-archaic-greece", "w-classical-greece")
rng("w-classical-age", -480, -323); txt("w-classical-age", dt(-480), dt(-323))
par("w-classical-age", "w-classical-greece")
rng("w-hellenistic", -336, -146); txt("w-hellenistic", dt(-336), dt(-146))
par("w-hellenistic", "w-classical-greece")
rng("w-macedonian", -336, -301); txt("w-macedonian", dt(-336), dt(-301))
par("w-macedonian", "w-hellenistic")

rng("w-maya", -200, 1696); txt("w-maya", dt(-200), dt(1696))
par("w-maya", "w-america-precol")
rng("w-mesoamerica", 100, 1521); txt("w-mesoamerica", dt(100), dt(1521))
par("w-mesoamerica", "w-america-precol")
rng("w-andes", -900, 1533); txt("w-andes", dt(-900), dt(1533))
par("w-andes", "w-america-precol")

rng("w-africa-west", 700, 1599); txt("w-africa-west", dt(700), dt(1599))
par("w-africa-west", "w-old-world")
rng("w-africa-east", -300, 1599); txt("w-africa-east", dt(-300), dt(1599))
par("w-africa-east", "w-old-world")

rng("w-shang", -1600, -1046); txt("w-shang", dt(-1600), dt(-1046))
par("w-shang", "w-ancient-china")
rng("w-zhou", -1046, -221); txt("w-zhou", dt(-1046), dt(-221))
par("w-zhou", "w-ancient-china")
rng("w-spring-autumn", -770, -221); txt("w-spring-autumn", dt(-770), dt(-221))
par("w-spring-autumn", "w-ancient-china")
rng("w-han-tang", -202, 907); txt("w-han-tang", dt(-202), dt(907))
par("w-han-tang", "w-ancient-china")
rng("w-tang-song", 618, 1279); txt("w-tang-song", dt(618), dt(1279))
par("w-tang-song", "w-ancient-china")
rng("w-ming-qing", 1368, 1911); txt("w-ming-qing", dt(1368), dt(1911))
par("w-ming-qing", "w-ancient-china")
rng("w-korea", -500, 1910); txt("w-korea", dt(-500), dt(1910))
par("w-korea", "w-east-asia")
rng("w-japan", -500, 1913); txt("w-japan", dt(-500), dt(1913))
par("w-japan", "w-east-asia")

rng("w-roman-republic", -753, -27); txt("w-roman-republic", dt(-753), dt(-27))
par("w-roman-republic", "w-roman")
rng("w-roman-empire", -27, 395); txt("w-roman-empire", dt(-27), dt(395))
par("w-roman-empire", "w-roman")
rng("w-late-roman", 284, 476); txt("w-late-roman", dt(284), dt(476))
par("w-late-roman", "w-roman")
rng("w-punic-war", -264, -146); txt("w-punic-war", dt(-264), dt(-146))
par("w-punic-war", "w-roman")
rng("w-byzantium", 330, 1452); txt("w-byzantium", dt(330), dt(1452))
par("w-byzantium", "w-roman")

rng("w-post-roman-europe", 476, 999); txt("w-post-roman-europe", dt(476), dt(999))
par("w-post-roman-europe", "w-post-roman")
rng("w-early-islam", 610, 750); txt("w-early-islam", dt(610), dt(750))
par("w-early-islam", "w-post-roman")
rng("w-post-roman-asia", 600, 999); txt("w-post-roman-asia", dt(600), dt(999))
par("w-post-roman-asia", "w-post-roman")
rng("w-abbasid-golden", 750, 1258); txt("w-abbasid-golden", dt(750), dt(1258))
par("w-abbasid-golden", "w-post-roman")
rng("w-islamic-golden", 762, 1258); txt("w-islamic-golden", dt(762), dt(1258))
par("w-islamic-golden", "w-abbasid-golden")

rng("w-carolingian", 768, 987); txt("w-carolingian", dt(768), dt(987))
par("w-carolingian", "w-post-roman")
rng("w-crusades", 1095, 1291); txt("w-crusades", dt(1095), dt(1291))
par("w-crusades", "w-post-roman")
rng("w-mongol-empire", 1206, 1368); txt("w-mongol-empire", dt(1206), dt(1368))
par("w-mongol-empire", "w-medieval")
rng("w-medieval-islam", 1000, 1499); txt("w-medieval-islam", dt(1000), dt(1499))
par("w-medieval-islam", "w-medieval")
rng("w-medieval-china", 960, 1368); txt("w-medieval-china", dt(960), dt(1368))
par("w-medieval-china", "w-medieval")

rng("w-italian-renaissance", 1300, 1499); txt("w-italian-renaissance", dt(1300), dt(1499))
par("w-italian-renaissance", "w-renaissance")
rng("w-northern-renaissance", 1500, 1599); txt("w-northern-renaissance", dt(1500), dt(1599))
par("w-northern-renaissance", "w-renaissance")

rng("w-age-of-sail", 1492, 1619); txt("w-age-of-sail", dt(1492), dt(1619))
par("w-age-of-sail", "w-early-modern")
rng("w-scientific-revolution", 1543, 1699); txt("w-scientific-revolution", dt(1543), dt(1699))
par("w-scientific-revolution", "w-early-modern")
rng("w-absolute-monarchy", 1500, 1749); txt("w-absolute-monarchy", dt(1500), dt(1749))
par("w-absolute-monarchy", "w-early-modern")

rng("w-industrial-rev", 1750, 1869); txt("w-industrial-rev", dt(1750), dt(1869))
par("w-industrial-rev", "w-modern")
rng("w-imperialism", 1870, 1913); txt("w-imperialism", dt(1870), dt(1913))
par("w-imperialism", "w-modern")
rng("w-world-wars", 1914, 1945); txt("w-world-wars", dt(1914), dt(1945))
par("w-world-wars", "w-modern")

rng("w-cold-war", 1945, 1990); txt("w-cold-war", dt(1945), dt(1990))
par("w-cold-war", "w-contemporary")
rng("w-decolonization", 1945, 1975); txt("w-decolonization", dt(1945), dt(1975))
par("w-decolonization", "w-contemporary")
rng("w-post-70s", 1975, 2026); txt("w-post-70s", dt(1975), dt(2026))
par("w-post-70s", "w-contemporary")
rng("w-tech-era", 1945, 2026); txt("w-tech-era", dt(1945), dt(2026))
par("w-tech-era", "w-contemporary")

rng("w-paleolithic", -3000000, -10000); txt("w-paleolithic", dt(-3000000), dt(-10000))
par("w-paleolithic", "w-prehistory")
rng("w-neolithic", -10000, -3001); txt("w-neolithic", dt(-10000), dt(-3001))
par("w-neolithic", "w-prehistory")

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
    if x["startYear"] > x["endYear"]:
        print("ORDER", x["id"]); bad += 1
roots = sorted([x for x in d if x.get("parentId") is None], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
for r in roots:
    print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))

def depth(x, seen=None):
    if seen is None: seen = set()
    p = x.get("parentId")
    if p is None: return 1
    if p in seen: return 99
    seen.add(x["id"])
    return 1 + depth(pidx[p], seen)
print("max depth:", max(depth(x) for x in d))
