# -*- coding: utf-8 -*-
"""Restructure period tree per Lead's spec:

Chronological spine (tags: 编年主干) - strictly contiguous, non-overlapping:
  w-prehistory        -3000000 .. -3600
  w-ancient-near-east   -3600 ..  -800
  w-classical-greece    -800 ..  -146
  w-roman               -753 ..   476
  w-post-roman           476 ..  1000
  w-medieval            1000 ..  1300
  w-renaissance         1300 ..  1600
  w-early-modern        1600 ..  1800
  w-modern              1800 ..  1914
  w-contemporary        1914 ..  2026

Regional branches (tags: 区域专题) - may overlap the spine:
  w-ancient-south-asia (ancient India)   -3000 .. -185
  w-ancient-china      (ancient China)    -1600 .. 1912
  w-old-world          (ancient Africa)   -3000 ..  1599
  w-america-precol     (pre-Columbian)   -2000 ..  1696
"""
import io, json, os

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_periods.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}


def dt(y):
    return ("公元前%d年" % (-y)) if y < 0 else ("公元%d年" % y)


def setp(pid, s, e, parent=None, name=None, alias=None):
    x = idx[pid]
    x["startYear"] = s
    x["endYear"] = e
    x["startDateText"] = dt(s)
    x["endDateText"] = dt(e)
    if parent is not None:
        x["parentId"] = parent
    elif parent is None and "parentId" in x:
        x["parentId"] = None
    if name:
        x["name"] = name
    if alias is not None:
        x["alias"] = alias
    return x


def tag(x, t):
    x["tags"] = list(dict.fromkeys((x.get("tags") or []) + [t]))


def untag(x, t):
    x["tags"] = [i for i in (x.get("tags") or []) if i != t]


# ============ rename ancient india -> ancient south asia ============
x = idx["w-ancient-india"]
x["name"] = "古代南亚"
x["alias"] = "古印度与南亚文明"
x["id"] = "w-ancient-south-asia"
del idx["w-ancient-india"]
idx["w-ancient-south-asia"] = x
for p in d:
    if p.get("parentId") == "w-ancient-india":
        p["parentId"] = "w-ancient-south-asia"

# ============ SPINE ============
setp("w-prehistory", -3000000, -3600, None)
setp("w-ancient-near-east", -3600, -800, None)
setp("w-classical-greece", -800, -146, None)
setp("w-roman", -753, 476, None)
setp("w-post-roman", 476, 1000, None)
setp("w-medieval", 1000, 1300, None)
setp("w-renaissance", 1300, 1600, None)
setp("w-early-modern", 1600, 1800, None)
setp("w-modern", 1800, 1914, None)
setp("w-contemporary", 1914, 2026, None)

# ============ REGIONAL ROOTS ============
setp("w-ancient-south-asia", -3000, -185, None, "古代南亚", "古印度与南亚文明")
setp("w-ancient-china", -1600, 1912, None, "古代中国", "商周至清末的中国")
setp("w-old-world", -3000, 1599, None, "古代非洲", "撒哈拉以南与北非的古代文明")
setp("w-america-precol", -2000, 1696, None, "前哥伦布美洲", "玛雅、阿兹特克与印加")

for pid in ("w-prehistory", "w-ancient-near-east", "w-classical-greece", "w-roman",
            "w-post-roman", "w-medieval", "w-renaissance", "w-early-modern",
            "w-modern", "w-contemporary"):
    untag(idx[pid], "区域专题")
    tag(idx[pid], "编年主干")
for pid in ("w-ancient-south-asia", "w-ancient-china", "w-old-world", "w-america-precol"):
    untag(idx[pid], "编年主干")
    tag(idx[pid], "区域专题")

# ============ sub-periods re-homed & re-ranged ============
# prehistory children
setp("w-paleolithic", -3000000, -10000, "w-prehistory")
setp("w-neolithic", -10000, -3601, "w-prehistory")

# ancient near east children (must fit -3600..-800)
setp("w-sumer", -3500, -2334, "w-ancient-near-east")
setp("w-akkad", -2334, -2154, "w-ancient-near-east")
setp("w-old-babylon", -1894, -1595, "w-ancient-near-east")
setp("w-assyrian", -2025, -609, "w-ancient-near-east")
setp("w-neobabylonian", -626, -539, "w-ancient-near-east")
setp("w-egypt-old", -3100, -332, "w-ancient-near-east")
setp("w-near-east-persian", -550, -330, "w-ancient-near-east")

# south asia children
setp("w-indus", -2600, -1900, "w-ancient-south-asia")
setp("w-aryan", -1500, -600, "w-ancient-south-asia")
setp("w-maurya", -322, -185, "w-ancient-south-asia")

# ancient china children + NEW china-history-aligned sub-nodes
setp("w-shang", -1600, -1046, "w-ancient-china")
setp("w-zhou", -1046, -221, "w-ancient-china")
setp("w-spring-autumn", -770, -221, "w-ancient-china")
setp("w-han-tang", -202, 907, "w-ancient-china")
setp("w-tang-song", 618, 1279, "w-ancient-china")
setp("w-ming-qing", 1368, 1911, "w-ancient-china")
setp("w-east-asia", -500, 1912, "w-ancient-china")
setp("w-korea", -500, 1910, "w-east-asia")
setp("w-japan", -500, 1913, "w-east-asia")

# greek children (-800..-146)
setp("w-archaic-greece", -800, -480, "w-classical-greece")
setp("w-classical-age", -480, -323, "w-classical-greece")
setp("w-hellenistic", -336, -146, "w-classical-greece")
setp("w-macedonian", -336, -301, "w-hellenistic")
setp("w-minoan", -3000, -1450, "w-classical-greece")
setp("w-mycenaean", -1750, -1100, "w-classical-greece")

# roman children (-753..476)
setp("w-roman-republic", -753, -27, "w-roman")
setp("w-roman-empire", -27, 395, "w-roman")
setp("w-late-roman", 284, 476, "w-roman")
setp("w-punic-war", -264, -146, "w-roman")

# post-roman children (476..1000)
setp("w-post-roman-europe", 476, 999, "w-post-roman")
setp("w-early-islam", 610, 750, "w-post-roman")
setp("w-post-roman-asia", 600, 999, "w-post-roman")
setp("w-abbasid-golden", 750, 999, "w-post-roman")
setp("w-islamic-golden", 762, 999, "w-abbasid-golden")
setp("w-carolingian", 768, 987, "w-post-roman")

# medieval children (1000..1300)
setp("w-crusades", 1095, 1291, "w-medieval")
setp("w-mongol-empire", 1206, 1300, "w-medieval")
setp("w-medieval-islam", 1000, 1300, "w-medieval")
setp("w-medieval-china", 1000, 1300, "w-medieval")
setp("w-byzantium", 1000, 1300, "w-medieval")

# renaissance children (1300..1600)
setp("w-italian-renaissance", 1300, 1499, "w-renaissance")
setp("w-northern-renaissance", 1500, 1600, "w-renaissance")

# early-modern children (1600..1800)
setp("w-age-of-sail", 1600, 1700, "w-early-modern")
setp("w-scientific-revolution", 1600, 1700, "w-early-modern")
setp("w-absolute-monarchy", 1600, 1749, "w-early-modern")
setp("w-southeast-asia", 1600, 1800, "w-early-modern")
setp("w-oceania", 1600, 1800, "w-early-modern")

# modern children (1800..1914)
setp("w-industrial-rev", 1800, 1870, "w-modern")
setp("w-imperialism", 1870, 1913, "w-modern")

# contemporary children (1914..2026)
setp("w-world-wars", 1914, 1945, "w-contemporary")
setp("w-cold-war", 1945, 1990, "w-contemporary")
setp("w-decolonization", 1945, 1975, "w-contemporary")
setp("w-post-70s", 1975, 2026, "w-contemporary")
setp("w-tech-era", 1945, 2026, "w-contemporary")

# africa children
setp("w-africa-west", 700, 1599, "w-old-world")
setp("w-africa-east", -300, 1599, "w-old-world")

# americas children
setp("w-maya", -200, 1696, "w-america-precol")
setp("w-mesoamerica", 100, 1521, "w-america-precol")
setp("w-andes", -900, 1533, "w-america-precol")

# ============ NEW china-aligned sub-periods (ids match china.json convention) ============
def mk(pid, name, alias, s, e, parent, color, summary, territory, capital, population, culture, tags):
    obj = {
        "id": pid, "name": name, "alias": alias, "parentId": parent,
        "startYear": s, "endYear": e, "startDateText": dt(s), "endDateText": dt(e),
        "colorKey": color, "summary": summary, "territory": territory, "capital": capital,
        "population": population, "culture": culture,
        "keyFigures": [], "relatedEvents": [], "tags": tags,
    }
    d.append(obj)
    idx[pid] = obj
    return obj


mk("w-cn-han", "汉", "西汉与东汉", -202, 220, "w-ancient-china", "han",
   "中国两千年大一统体制的奠基时期，与罗马帝国、贵霜王朝、安息帝国并立于欧亚大陆的东西两端。公元前202年刘邦建立汉朝，承秦制而变之，以郡国并行、休养生息与独尊儒术奠定此后两千年政治文化的基本格局；汉武帝时推恩令、罢黜百家独尊儒术、卫青霍去病北击匈奴、张骞凿空西域，使汉朝疆域扩展至河西走廊与西域都护府辖区，丝绸之路由此贯通欧亚，与大秦、安息、大月氏的往来日益密切。东汉时期佛教传入中国，白马寺的建立成为中外宗教交流的标志性起点。",
   "西至葱岭与西域都护府辖区，东至东海，南至南海，北至长城与阴山", "长安、洛阳", "约1500万至6000万",
   "郡县与中央集权；儒学独尊与经学；张骞凿空西域与丝绸之路；造纸术发明；佛教传入与白马寺；编户齐民与编年史",
   ["汉朝", "丝绸之路", "中国史对照"])

mk("w-cn-tang", "唐", "唐朝", 618, 907, "w-ancient-china", "sui-tang",
   "中国古代 worlds 的盛世之一，也是当时东亚乃至世界秩序的枢纽。唐朝以科举取士、均田租庸调与三省六部制构成当时世界上最完备的国家体制，长安成为人口逾百万的欧亚第一大都会，胡商云集，来自波斯、粟特、阿拉伯、日本与印度的使节、留学生与僧侣汇集于此。玄奘西行与义净东归带回大量梵文佛经，鉴真东渡日本建立唐招提寺；雕版印刷在唐代出现，造纸术经中亚传入伊斯兰世界，日本的遣唐使把唐律、书法与工艺系统带入日本。同期怛罗斯之战后造纸术西传，成为中国与伊斯兰世界、欧洲之间技术与文明交流的关键节点之一。",
   "东至朝鲜半岛南部，南至越南中部，西至安西四镇，北至长城与单于庭", "长安、洛阳", "约4000万至8000万",
   "科举与三省六部；唐诗与乐舞；佛教传播与译经；雕版印刷；长安国际都市；朝贡贸易与丝路西传",
   ["唐朝", "丝路西传", "中国史对照"])

mk("w-cn-song", "宋", "北宋与南宋", 960, 1279, "w-ancient-china", "yellow",
   "中国古代社会大转型的时期，与欧洲中世纪盛期、伊斯兰世界的中世纪全盛并行。宋代农业技术、水利与稻麦复种制推广使单位面积产量提高，耕织结合的小农经济与市场化手工业、成熟商税与纸币体系使城市与长途贸易空前繁荣，开封与临安成为当时世界最大的城市；印刷术、火药、指南针与造船技术在此成熟并向外输出，理学与心学提供了新的思想框架。同期辽、金、西夏与蒙古在北方并立，构成中国史上罕见的多元政权格局；海上贸易与市舶制度使泉州、广州成为海上丝绸之路枢纽，日本的禅宗与朱子学传入东亚。",
   "宋辽金西夏并立的中国，南至海南，北抵幽云，西限陇右", "开封、临安（杭州）、兴庆（北京大都）", "约8000万至1.3亿",
   "商业革命与纸币；印刷术与火药指南针；理学与心学；市舶贸易；词与话本；辽金西夏多元政权",
   ["宋朝", "唐宋变革", "中国史对照"])

mk("w-cn-ming", "明", "明朝", 1368, 1644, "w-ancient-china", "pink",
   "中国最后一个王朝的前半期，也是 15 世纪世界海洋秩序的重要参与者。1368年朱元璋逐元北伐攻克大都，1403年朱棣迁都北京并派郑和七下西洋（1405—1433年），船队抵达东南亚、印度、阿拉伯半岛与东非，是当时世界上规模最大的远洋航行，使明朝成为印度洋地区最可见的国家。此后转向北方长城防线与白银输入，一条鞭法与白银货币化深刻影响中国经济。海禁与朝贡体系并行，日本的织田与丰臣完成统一并进入江户锁国，欧洲则开始大航海与早期殖民，三大区域的贸易网络由此交汇。",
   "北至长城与奴儿干，南至海南与旧港，西至嘉峪关，东至朝鲜半岛", "南京、北京", "约6000万至1.5亿",
   "一条鞭法与白银货币化；郑和下西洋；朝贡与海禁；紫禁城与园林；四大名著与昆曲；京杭大运河",
   ["明朝", "郑和下西洋", "中国史对照"])

mk("w-cn-qing", "清", "清朝", 1644, 1912, "w-ancient-china", "qing",
   "中国最后一个王朝的后半期，疆域达到传统中国的最大范围。1644年李自成入北京、吴三桂引清兵入关，清朝取代明朝并确立摊丁入亩、圈地与册旗等制度；康乾之世维持了稳定与繁荣，人口从一亿增至三亿，白银从美洲与日本大量流入使中国成为当时世界贸易网络的核心节点之一。制度上，中国以科举与儒家经典维持统治，与同时期的欧洲启蒙运动、日本的町人经济、印度的莫卧儿宫廷形成有趣的对照；工业革命后中国被迫开放口岸，1894年甲午战争与1911年辛亥革命终结了帝制。",
   "北至黑龙江与外兴安岭，西跨葱岭与巴尔喀什湖，南至海南与台湾，西藏与新疆纳入版图", "北京", "约1亿至4亿",
   "摊丁入亩与丁银；军机处与文字狱；闭关与开埠；康乾人口增长；金瓶掣签与边疆治理；洋务与新政",
   ["清朝", "康乾盛世", "中国史对照"])

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- validate ----
ids = [x["id"] for x in d]
assert len(ids) == len(set(ids)), "dup ids"
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
    if x["startYear"] > x["endYear"]:
        print("ORDER", x["id"]); bad += 1
roots = sorted([x for x in d if x.get("parentId") is None], key=lambda z: z["startYear"])
print("total:", len(d), "roots:", len(roots), "issues:", bad)
print("--- spine (编年主干) ---")
for r in roots:
    if "编年主干" in (r.get("tags") or []):
        print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
print("--- regional (区域专题) ---")
for r in roots:
    if "区域专题" in (r.get("tags") or []):
        print("   %-20s %8d..%6d  %s" % (r["id"], r["startYear"], r["endYear"], r["name"]))
