"""世界史事件的时期归位。

两类问题：
1. 跨文明专题事件（ev-cc-*）原先散落在「朝鲜半岛」等区域专题下。
   这类事件没有单一文明归属，集中挂到「跨文明交流」专题线，
   并按时代拆成子时期——否则一个横跨十万年的色块在时间轴上没法用。
2. 中国史事件（ev-qin-*、ev-han-*、ev-sui-tang 等）被年份归位
   错放进东亚的区域专题，应落到世界史里的中国主线时期。

关键约束：任何归位都必须通过**年份守卫**——目标时期的
[startYear, endYear] 必须真的包含事件的 year（负数=公元前，
数值小=更早）。之前用朴素字符串前缀匹配，把《汉谟拉比法典》
当成汉朝事件塞进汉唐时期，就是缺了这道守卫。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

CROSS_CIV_ID = "w-cross-civilization"
CROSS_CIV_NAME = "跨文明交流"

# 跨文明线的时代分段：(子时期 id, 名称, 起始年, 结束年, 概述)
CROSS_CIV_ERAS = [
    ("w-cc-prehistoric", "史前全球联系", -100100, -3001,
     "智人走出非洲与全球扩散、作物与家畜的独立驯化、语言与技术的跨大陆传播。"
     "这一阶段的「联系」以迁徙与扩散为主，尚无稳定的跨洲贸易网络。"),
    ("w-cc-classical", "古典跨文明网络", -3000, 500,
     "三大古典文明同时兴起，草原丝路与季风航线把欧亚非连成松散网络。"
     "文字、宗教、冶铁与马匹沿这些通道流动，犍陀罗艺术是希腊与佛教交汇的产物。"),
    ("w-cc-medieval", "中古跨文明网络", 501, 1500,
     "伊斯兰世界成为东西贸易的中间人，印度洋季风贸易成熟。"
     "造纸术、火药、指南针与黑死病先后沿商路跨洲传播，蒙古治世短暂打通了欧亚。"),
    ("w-cc-oceanic", "大航海与全球贸易", 1501, 1800,
     "绕过好望角与横渡大西洋的航线把四大洲连成一体。"
     "哥伦布大交换重组了各洲的作物、人口与生态，白银把美洲、欧洲与亚洲串成一条链。"),
    ("w-cc-industrial", "工业时代的全球联系", 1801, 1945,
     "蒸汽船、铁路与海底电报把全球通讯压缩到小时级。"
     "殖民体系把亚非拉纳入单一市场，同时也催生了反殖民的民族运动。"),
    ("w-cc-contemporary", "当代全球化", 1946, 2026,
     "布雷顿森林体系、集装箱运输与互联网重塑了全球分工。"
     "气候协定、 pandemic 与人工智能把人类共同问题推到前台。"),
]

# 中国史事件 → 世界史中国主线时期。只在年份守卫通过时生效。
CN_EVENT_RULES = [
    ("ev-qin-", "w-ancient-china"),
    ("ev-zhou-", "w-ancient-china"),
    ("ev-xia-", "w-ancient-china"),
    ("ev-shang-", "w-ancient-china"),
    ("ev-han-zhangqian", "w-han-tang"),
    ("ev-han-wudi", "w-han-tang"),
    ("ev-han-buddhism", "w-han-tang"),
    ("ev-han-founding", "w-han-tang"),
    ("ev-han-end", "w-han-tang"),
    ("ev-sui-tang", "w-han-tang"),
    ("ev-three-kingdoms", "w-han-tang"),
    ("ev-jin-unify-nanbeiguo", "w-han-tang"),
    ("ev-song-jin-", "w-tang-song"),
    ("ev-med-kor-goryeo", "w-korea"),
]


def year_ok(period, y):
    """事件年份是否落在时期区间内（负数=公元前，数值小=更早）。"""
    if not isinstance(y, int):
        return False
    ps, pe = period.get("startYear"), period.get("endYear")
    if not isinstance(ps, int) or not isinstance(pe, int):
        return False
    return ps <= y <= pe


def fmt_year(y):
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def ensure_cross_civ(periods, events):
    """建立跨文明专题线及其时代子时期，并把 ev-cc-* 挂到对应子时期。"""
    cc = [e for e in events if e.get("id", "").startswith("ev-cc-")]
    if not cc:
        return 0

    by_id = {p["id"]: p for p in periods}

    # ---- 父时期：覆盖全域，本身不挂事件 ----
    parent = by_id.get(CROSS_CIV_ID)
    if parent is None:
        parent = {
            "id": CROSS_CIV_ID,
            "name": CROSS_CIV_NAME,
            "alias": "全球联系",
            "parentId": None,
            "startYear": CROSS_CIV_ERAS[0][2],
            "endYear": CROSS_CIV_ERAS[-1][3],
            "startDateText": fmt_year(CROSS_CIV_ERAS[0][2]),
            "endDateText": fmt_year(CROSS_CIV_ERAS[-1][3]),
            "colorKey": "earlymodern",
            "summary": (
                "跨文明交流把散见于各文明史中的「连接性事件」聚到一条线索上："
                "迁徙与扩散、丝绸之路与季风航路、宗教与文字的传播、技术与作物的跨洲流动，"
                "以及大航海之后的全球贸易网络。它不替代任何文明自身的编年，"
                "而是提供另一个角度——同一个世纪里，不同文明之间发生了什么。"
            ),
            "territory": "欧亚非大陆及其海上航线",
            "capital": "—",
            "population": "—",
            "culture": "迁徙、丝路、季风贸易、宗教传播、技术西传、白银与作物交换",
            "keyFigures": [],
            "relatedEvents": [],
            "tags": ["区域专题", "跨文明", "全球联系"],
        }
        periods.append(parent)

    # ---- 子时期 ----
    for pid, name, lo, hi, summary in CROSS_CIV_ERAS:
        if pid in by_id:
            continue
        child = {
            "id": pid,
            "name": name,
            "alias": "",
            "parentId": CROSS_CIV_ID,
            "startYear": lo,
            "endYear": hi,
            "startDateText": fmt_year(lo),
            "endDateText": fmt_year(hi),
            "colorKey": "earlymodern",
            "summary": summary,
            "territory": "欧亚非与美洲",
            "capital": "—",
            "population": "—",
            "culture": "跨洲贸易、宗教与技术传播",
            "keyFigures": [],
            "relatedEvents": [],
            "tags": ["跨文明"],
        }
        periods.append(child)
        by_id[pid] = child

    # ---- 按年份把事件分到子时期 ----
    unassigned = []
    moved = 0
    for e in cc:
        y = e.get("year")
        target = None
        for pid, _name, lo, hi, _s in CROSS_CIV_ERAS:
            if isinstance(y, int) and lo <= y <= hi:
                target = pid
                break
        if target is None:
            unassigned.append((e["id"], y))
            continue
        if e.get("periodId") != target:
            e["periodId"] = target
            moved += 1

    # ---- 用实际事件的年份范围回算各子时期区间 ----
    # 跨年度事件（year..yearEnd 跨过时代边界）会让 yearEnd 落到区间外，
    # 因此按子时期实际承载的事件重新收紧/放宽区间。兄弟时期允许交叠。
    spans = {}
    for e in cc:
        pid = e.get("periodId")
        y, ye = e.get("year"), e.get("yearEnd")
        if pid not in {p for p, *_ in CROSS_CIV_ERAS}:
            continue
        if not isinstance(y, int):
            continue
        lo = y
        hi = ye if isinstance(ye, int) and ye >= y else y
        if pid in spans:
            a, b = spans[pid]
            spans[pid] = (min(a, lo), max(b, hi))
        else:
            spans[pid] = (lo, hi)

    for pid, (lo, hi) in spans.items():
        child = by_id.get(pid)
        if child is None:
            continue
        child["startYear"] = min(lo, child.get("startYear", lo))
        child["endYear"] = max(hi, child.get("endYear", hi))
        child["startDateText"] = fmt_year(child["startYear"])
        child["endDateText"] = fmt_year(child["endYear"])

    # ---- 父时期覆盖全部子时期 ----
    if spans:
        child_los = [by_id[p]["startYear"] for p in spans if p in by_id]
        child_his = [by_id[p]["endYear"] for p in spans if p in by_id]
        parent["startYear"] = min(child_los)
        parent["endYear"] = max(child_his)
        parent["startDateText"] = fmt_year(parent["startYear"])
        parent["endDateText"] = fmt_year(parent["endYear"])

    print(f"  cross-civ: {len(cc)} events, moved {moved}, "
          f"unassigned {len(unassigned)}, spans={len(spans)}")
    for u in unassigned[:6]:
        print(f"     unassigned {u[0]} year={u[1]}")
    return moved


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    periods = d["periods"]
    events = d["events"]

    ensure_cross_civ(periods, events)

    # ---- 中国史事件归位（带年份守卫）----
    by_id = {x["id"]: x for x in periods}
    cn_moved = 0
    skipped = []
    for e in events:
        eid = e.get("id", "")
        if eid.startswith("ev-cc-"):
            continue
        target = None
        for pref, pid in CN_EVENT_RULES:
            if eid.startswith(pref) and pid in by_id:
                target = pid
                break
        if not target or target == e.get("periodId"):
            continue
        if year_ok(by_id[target], e.get("year")):
            e["periodId"] = target
            cn_moved += 1
        else:
            skipped.append((eid, e.get("year"), target))
    print(f"  china events in world: moved {cn_moved}, "
          f"guard-skipped {len(skipped)}")
    for s in skipped[:6]:
        print(f"     skip {s[0]} (year={s[1]}) -> {s[2]}")

    # ---- 报告 ----
    outside = 0
    for e in events:
        p2 = by_id.get(e.get("periodId"))
        if p2 and isinstance(e.get("year"), int) and not year_ok(p2, e["year"]):
            outside += 1
    print(f"  events outside their period: {outside}")

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
