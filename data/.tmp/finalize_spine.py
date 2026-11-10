# -*- coding: utf-8 -*-
"""Apply Lead's exact spine spec. Rome = -753..476 (7yr overlap with Greece
is explicitly permitted). Re-home Roman-era children accordingly."""
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


# Lead's exact spine
setp("w-roman", -753, 476, None)

# Roman children must fit -753..476 now
setp("w-roman-republic", -753, -27, "w-roman")
setp("w-roman-empire", -27, 395, "w-roman")
setp("w-late-roman", 284, 476, "w-roman")
setp("w-punic-war", -264, -146, "w-roman")
setp("w-neobabylonian", -753, -539, "w-roman")

# these had been moved to classical-greece under the old scheme; restore
setp("w-egypt-old", -3600, -332, "w-ancient-near-east")
setp("w-near-east-persian", -550, -330, "w-ancient-near-east")
setp("w-assyrian", -2025, -609, "w-ancient-near-east")
setp("w-minoan", -3000, -1450, "w-ancient-near-east")
setp("w-mycenaean", -1750, -1100, "w-ancient-near-east")

# classical-greece children must fit -800..-146
setp("w-archaic-greece", -800, -480, "w-classical-greece")
setp("w-classical-age", -480, -323, "w-classical-greece")
setp("w-hellenistic", -336, -146, "w-classical-greece")
setp("w-macedonian", -336, -301, "w-hellenistic")

# byzantium 330..1452 doesn't fit post-roman/medieval -> split into two nodes
bx = idx["w-byzantium"]
bx["name"] = "拜占庭帝国（中古）"
bx["alias"] = "东罗马帝国"
setp("w-byzantium", 1000, 1300, "w-medieval")

# add early/late byzantine nodes so the 330-476 and 1300-1452 spans are covered
def mk(pid, name, alias, s, e, parent, color, summary, tags):
    obj = {
        "id": pid, "name": name, "alias": alias, "parentId": parent,
        "startYear": s, "endYear": e, "startDateText": dt(s), "endDateText": dt(e),
        "colorKey": color, "summary": summary,
        "territory": "小亚细亚、叙利亚、埃及、希腊、意大利南部、克里米亚",
        "capital": "君士坦丁堡、尼西亚", "population": "约1000万至3000万",
        "culture": "《民法大全》；圣索菲亚与拜占庭圣像；东正教；希腊学术；宫廷礼仪",
        "keyFigures": [], "relatedEvents": [], "tags": tags,
    }
    d.append(obj)
    idx[pid] = obj


if "w-byzantium-early" not in idx:
    mk("w-byzantium-early", "晚期罗马帝国与早期拜占庭", "君士坦丁帝国", 284, 476, "w-roman", "rome",
       "戴克里先改革、君士坦丁的基督教化与君士坦丁堡的建立，构成罗马帝国晚期向拜占庭帝国过渡的关键阶段。戴克里先的四帝共治与税制、军制改革重整了帝国；313年君士坦丁在米兰敕令中给予基督教合法地位，325年尼西亚公会议定《尼西亚信经》，330年迁都拜占庭并改名君士坦丁堡。狄奥多西一世后帝国分为东西，476年西罗马帝国终结。晚期帝国在法制、财政与宗教制度上的调整为中世纪欧洲的封建制度与拜占庭的延续奠定基础。",
       ["拜占庭", "晚期罗马", "基督教"])

if "w-byzantium-late" not in idx:
    mk("w-byzantium-late", "拜占庭晚期与君士坦丁堡的陷落", "东罗马末期", 1300, 1452, "w-renaissance", "medieval",
       "拜占庭帝国在十字军冲击与奥斯曼压力下的最后阶段。1204年第四次十字军攻陷君士坦丁堡是致命打击，城市在拉丁人的统治下中断了半个多世纪；1261年拜占庭复国后米海尔八世与安纳托利亚的奥斯曼结盟以换取支持，却引狼入室；1321年奥斯曼在小亚细亚建国，1362年攻占君士坦丁堡并逐步经营欧洲部分。拜占庭的学者在帝国末期大量流往意大利与阿拉伯世界，其希腊学术传统与古抄本成为文艺复兴的重要资源。1453年5月奥斯曼军攻陷君士坦丁堡，末代皇帝君士坦丁十一世战死，延续两千余年的罗马帝国就此终结。",
       ["拜占庭", "1453", "奥斯曼", "东罗马"])

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pidx = {x["id"]: x for x in d}
bad = 0
for x in d:
    p = x.get("parentId")
    if p is None: continue
    if p not in pidx:
        print("DANGLING", x["id"], p); bad += 1; continue
    pr = pidx[p]
    if pr["startYear"] > x["startYear"] or x["endYear"] > pr["endYear"]:
        print("RANGE", x["id"], x["startYear"], x["endYear"], "| p", p, pr["startYear"], pr["endYear"]); bad += 1
roots = [x for x in d if x.get("parentId") is None]
spine = sorted([r for r in roots if "编年主干" in (r.get("tags") or [])], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
print("SPINE:")
for r in spine:
    print("   %-22s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
# overlap report
print("SPINE OVERLAPS:")
for a, b in zip(spine, spine[1:]):
    ov = min(a["endYear"], b["endYear"]) - max(a["startYear"], b["startYear"]) + 1
    if ov > 1:
        print("   %s / %s overlap %d years" % (a["id"], b["id"], ov))
