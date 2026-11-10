"""从已有数据推导并补全人物与事件之间的关联。

不做任何主观推测，只用两种**数据里已经存在**的事实：

1. 共同参与同一事件 → 互为相关人物。
   若事件 E 的 figures 为 [A, B, C]，则 A/B/C 彼此相关，
   且每人的 relatedEvents 都包含 E。

2. 正文互相提及 → 建立关联。
   事件正文里出现某位同时代人物的姓名，就把该人物挂到事件上；
   人物传记里出现某事件的名称，就把该事件挂到人物上。
   这类匹配以「同一时期内」为限，避免误连。

关联数量设上限，防止单个人物挂上几十条导致页面失衡。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

MAX_COFIG = 12        # 每人最多保留的相关人物
MAX_EVENTS = 20       # 每人最多保留的相关事件
MAX_EV_FIGS = 12      # 每个事件最多保留的涉及人物
YEAR_WINDOW = 150     # 跨主线关联时允许的年代差
YEAR_GUARD = 400     # 事件与人物之间允许的最大年代差


def name_ok(name):
    """只对足够长的中文姓名做正文匹配，避免单字误命中。"""
    return isinstance(name, str) and len(name) >= 2 and re.search(r"[\u4e00-\u9fff]", name)


# 事件名里的连接词与描述性字样，切词时去掉
_EVENT_NOISE = (
    "与和的及、与" "在" "的" "与" "和" "及" "等" "由" "从" "到" "于" "中"
    "前" "后" "时期" "时代" "世纪" "王朝" "运动" "战争" "革命" "形成"
    "建立" "兴起" "衰落" "崩溃" "覆灭" "瓦解" "整合" "重组" "转型"
    "条件下" "环境" "条件下形成" "过程" "影响" "作用" "意义" "价值"
    "之一" "及其" "及其对" "对" "为" "使" "并" "而" "则" "其" "之"
    "第一" "第二" "第三" "大规模" "全面" "重要" "主要" "核心"
    "早期" "中期" "晚期" "近代" "古代" "现代" "当代" "中古" "上古"
)


def event_keywords(event_name):
    """从事件名里抽出可用于正文匹配的关键词。

    事件名往往很长（「彼特拉克与欧洲人文主义的兴起」），
    传记里不会逐字包含，但其中的名词性短语（「人文主义」）会��
    所以这里按连接词切分，取长度足够的片段作为关键词。
    """
    if not isinstance(event_name, str) or len(event_name) < 4:
        return ()
    parts = re.split(r"[与和及的、，,（(）)「」]", event_name)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 3 or not re.search(r"[\u4e00-\u9fff]", p):
            continue
        # 去掉尾部常见的描述性成分
        changed = True
        while changed:
            changed = False
            for noise in _EVENT_NOISE:
                if p.endswith(noise) and len(p) - len(noise) >= 3:
                    p = p[: -len(noise)]
                    changed = True
            # 「赤壁之」这类以「之」结尾的残片，剥掉后若仍够长就保留
            if p.endswith("之") and len(p) > 3:
                p = p[:-1]
                changed = True
        if len(p) >= 3 and re.search(r"[\u4e00-\u9fff]", p):
            out.append(p)
    return tuple(out)


def same_period_group(periods_by_id, a, b):
    """两个时期是否属于同一条主线或父子关系（放宽到顶层祖先相同）。"""
    if a == b:
        return True
    pa, pb = periods_by_id.get(a), periods_by_id.get(b)
    if not pa or not pb:
        return False
    return pa.get("parentId") == pb.get("parentId")


def top_ancestor(periods_by_id, pid):
    node = periods_by_id.get(pid)
    seen = set()
    while node and node.get("parentId") and node["id"] not in seen:
        seen.add(node["id"])
        nxt = periods_by_id.get(node["parentId"])
        if not nxt:
            break
        node = nxt
    return node["id"] if node else None


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    figs = {f["id"]: f for f in d.get("figures") or []}
    evs = {e["id"]: e for e in d.get("events") or []}
    pmap = {p["id"]: p for p in d.get("periods") or []}

    # 补齐空列表字段
    for f in figs.values():
        f.setdefault("relatedFigures", [])
        f.setdefault("relatedEvents", [])
    for e in evs.values():
        e.setdefault("figures", [])

    added_pair = 0
    added_ev = 0
    added_fig_to_ev = 0

    # ---- 1. 共同参与同一事件 ----
    for e in evs.values():
        members = [x for x in (e.get("figures") or []) if x in figs]
        for f in members:
            if e["id"] not in figs[f]["relatedEvents"]:
                figs[f]["relatedEvents"].append(e["id"])
                added_ev += 1
        for a in members:
            for b in members:
                if a == b:
                    continue
                if b not in figs[a]["relatedFigures"]:
                    figs[a]["relatedFigures"].append(b)
                    added_pair += 1

    # ---- 2. 正文互相提及 ----
    # 人物按顶层祖先分桶，但匹配时**不限定在同一主线内**：
    # 早期版本只在同一顶层时期内找人，导致世界史里跨文明的事件
    # （如「丝绸之路上的希腊化影响」）匹配不到提及的人物，
    # 事件往往一个涉及人物都没有。跨主线匹配由后面的
    # 「同主线或年代相近」守卫负责过滤掉不合理的组合。
    fig_by_top = {}
    for f in figs.values():
        t = top_ancestor(pmap, f.get("periodId"))
        fig_by_top.setdefault(t, []).append(f)

    all_figs = list(figs.values())

    for e in evs.values():
        text = (e.get("summary") or "") + (e.get("detail") or "")
        if not text:
            continue
        top = top_ancestor(pmap, e.get("periodId"))
        # 先看同一主线内的人，不够再放宽到全部人物
        pool = list(fig_by_top.get(top, []))
        if len(pool) < MAX_EV_FIGS:
            pool += [f for f in all_figs if f not in pool]
        hit = []
        existing = set(e.get("figures") or [])
        ev_year = e.get("year")
        for f in pool:
            nm = f.get("name")
            if not name_ok(nm) or f["id"] in existing:
                continue
            # 年代守卫：人物与事件的年代不能相差太远。
            # 放宽到跨主线匹配后，若不加这道限制，
            # 三国事件会因为提到「水」这类字面而挂上先秦人物。
            if isinstance(ev_year, int):
                fy = f.get("deathYear") if isinstance(f.get("deathYear"), int) \
                    else f.get("birthYear")
                if isinstance(fy, int) and abs(ev_year - fy) > YEAR_GUARD:
                    continue
            if nm in text:
                hit.append(f["id"])
        for fid in hit:
            if len(e["figures"]) >= MAX_EV_FIGS:
                break
            e["figures"].append(fid)
            added_fig_to_ev += 1
            if e["id"] not in figs[fid]["relatedEvents"]:
                figs[fid]["relatedEvents"].append(e["id"])
            for other in e["figures"]:
                if other == fid or other not in figs:
                    continue
                if other not in figs[fid]["relatedFigures"]:
                    figs[fid]["relatedFigures"].append(other)
                if fid not in figs[other]["relatedFigures"]:
                    figs[other]["relatedFigures"].append(fid)

    # ---- 3. 人物传记提到事件名 → 挂上事件 ----
    #
    # 事件名普遍很长（「彼特拉克与欧洲人文主义的兴起」有十二字），
    # 传记里几乎不会逐字包含，所以只按全名匹配基本匹配不到。
    # 这里再加上「关键词匹配」：取事件名里较长的名词性片段
    # （如「人文主义」「哥特式建筑」「活字印刷」），出现在传记里也算提及。
    for f in figs.values():
        bio = (f.get("biography") or "") + (f.get("summary") or "")
        if not bio:
            continue
        top = top_ancestor(pmap, f.get("periodId"))
        for e in evs.values():
            if top_ancestor(pmap, e.get("periodId")) != top:
                continue
            nm = e.get("name")
            if not name_ok(nm):
                continue
            if e["id"] in f["relatedEvents"]:
                continue
            if nm in bio or any(kw in bio for kw in event_keywords(nm)):
                f["relatedEvents"].append(e["id"])

    # ---- 4. 截断到上限，并清理自引用/悬空引用 ----
    # 同时做跨时代守卫：原始分片里存在用错 id 的情况
    # （例如某条三国事件错误引用了 fig-lu-xun-2，而该 id 实为鲁迅），
    # 若不加限制，孙权就会被挂上一条通往近代作家的荒谬关联。
    #
    # 判据放宽为「同一条主线」**或**「年代相近」——
    # 世界史有大量平行的文明支线，只要求同主线会把合理的关联也一并砍掉。
    def top(fid):
        return top_ancestor(pmap, figs[fid].get("periodId")) if fid in figs else None

    def figure_year(fid):
        f = figs.get(fid) or {}
        for k in ("deathYear", "birthYear"):
            v = f.get(k)
            if isinstance(v, int):
                return v
        return None

    def related_ok(a, b):
        if top(a) == top(b):
            return True
        ya, yb = figure_year(a), figure_year(b)
        if ya is None or yb is None:
            return False
        return abs(ya - yb) <= YEAR_WINDOW

    for f in figs.values():
        my_top = top(f["id"])
        rel_f = []
        for x in dict.fromkeys(f["relatedFigures"]):
            if x == f["id"] or x not in figs:
                continue
            if not related_ok(f["id"], x):
                continue
            rel_f.append(x)
        rel_e = [x for x in dict.fromkeys(f["relatedEvents"])
                 if x in evs and top_ancestor(pmap, evs[x].get("periodId")) == my_top]
        f["relatedFigures"] = rel_f[:MAX_COFIG]
        f["relatedEvents"] = rel_e[:MAX_EVENTS]

    for e in evs.values():
        e["figures"] = [x for x in dict.fromkeys(e.get("figures") or [])
                        if x in figs][:MAX_EV_FIGS]

    # 对称性保证：A 指向 B 时，B 也指向 A
    sym = 0
    for fid, f in figs.items():
        for other in list(f["relatedFigures"]):
            if fid not in figs[other]["relatedFigures"]:
                if len(figs[other]["relatedFigures"]) < MAX_COFIG:
                    figs[other]["relatedFigures"].append(fid)
                    sym += 1

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{path}: 新增人物-人物关联 {added_pair}，人物-事件关联 {added_ev}，"
          f"正文匹配补入事件人物 {added_fig_to_ev}，对称补齐 {sym}")


if __name__ == "__main__":
    main()
