"""修正两类与时期区间相关的数据问题。

A. 年份符号错误
   以 dateText 为权威还原 year / yearEnd。典型病例：
   ev-tang-dijianjie 存的是 year=-705、yearEnd=675（狄仁杰是唐人，
   两个数都应是公元），dateText 却写成「公元675年－公元前705年」。
   按 dateText 里的「公元／公元前」前缀重新取号后，再按真实先后排序，
   就能还原成 675—705 这一合理跨度。

B. 合法跨越多个子时期的事件
   「百家争鸣」公元前550年至前221年，横跨春秋与战国，落在任何单个
   子时期都会超出区间。这类事件应当挂到能完整容纳其跨度的**父时期**，
   而不是硬塞进某个子时期。沿 parentId 向上查找第一个能容纳的时期。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 匹配「公元N年」「公元前N年」
TOKEN = re.compile(r"公元前\s*(\d+)\s*年|公元\s*(\d+)\s*年")


def parse_tokens(text):
    """从 dateText 里按出现顺序取出年份（负数=公元前）。"""
    out = []
    for m in TOKEN.finditer(text or ""):
        if m.group(1) is not None:
            out.append(-int(m.group(1)))
        else:
            out.append(int(m.group(2)))
    return out


# 时期边界的史实校正：(时期 id, 新 startYear, 新 endYear)
# 战国结束于公元前221年秦统一，原数据写 -222，导致「秦统一」前后的事件
# 全部卡在区间外。隋朝建立于581年（原数据从589年灭陈算起）。
BOUNDARY_FIX = {
    "cn-warring-states": (None, -221),
    "cn-zhou-east": (None, -221),
    "cn-sui": (581, 618),
}


def apply_boundary_fix(by_id):
    """校正时期边界，并把父时期一并放宽以容纳子时期。"""
    changed = []
    for pid, (ns, ne) in BOUNDARY_FIX.items():
        p = by_id.get(pid)
        if p is None:
            continue
        if ns is not None and (p.get("startYear") is None or ns < p["startYear"]):
            p["startYear"] = ns
            p["startDateText"] = fmt(ns)
            changed.append(pid)
        if ne is not None and (p.get("endYear") is None or ne > p["endYear"]):
            p["endYear"] = ne
            p["endDateText"] = fmt(ne)
            changed.append(pid)

    # 父时期必须覆盖子时期
    for p in list(by_id.values()):
        node = p
        seen = set()
        while node is not None and node["id"] not in seen:
            seen.add(node["id"])
            pp = by_id.get(node.get("parentId"))
            if pp is None:
                break
            if p["startYear"] < pp["startYear"]:
                pp["startYear"] = p["startYear"]
                pp["startDateText"] = fmt(pp["startYear"])
            if p["endYear"] > pp["endYear"]:
                pp["endYear"] = p["endYear"]
                pp["endDateText"] = fmt(pp["endYear"])
            node = pp
    return changed


def year_ok(period, y):
    if not isinstance(y, int):
        return False
    ps, pe = period.get("startYear"), period.get("endYear")
    if not isinstance(ps, int) or not isinstance(pe, int):
        return False
    return ps <= y <= pe


def span_ok(period, y, ye):
    if not year_ok(period, y):
        return False
    return year_ok(period, ye) if isinstance(ye, int) else True


def fmt(y):
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    periods = d["periods"]
    by_id = {p["id"]: p for p in periods}

    fixed_sign = 0
    moved_up = 0
    clamped = 0
    unresolved = []

    # ---- 0. 时期边界的史实校正 ----
    changed = apply_boundary_fix(by_id)
    if changed:
        print(f"  boundary-fixed: {sorted(set(changed))}")

    for e in d.get("events") or []:
        eid = e.get("id", "")
        y, ye = e.get("year"), e.get("yearEnd")
        dt = e.get("dateText") or ""

        # ---- A. 以 dateText 为权威还原年份 ----
        toks = parse_tokens(dt)
        if toks and isinstance(y, int):
            # 两个年份一正一负、绝对值却相近（<200 年）时，
            # 说明负号是误加的——例如「公元675年－公元前705年」，
            # 675 与 705 相差 30 年，实为同一区间。
            if len(toks) >= 2 and toks[0] > 0 > toks[1] \
                    and abs(abs(toks[0]) - abs(toks[1])) < 200:
                toks = [abs(toks[0]), abs(toks[1])]
            elif len(toks) >= 2 and toks[1] > 0 > toks[0] \
                    and abs(abs(toks[0]) - abs(toks[1])) < 200:
                toks = [abs(toks[0]), abs(toks[1])]

            new_y = toks[0]
            new_ye = toks[1] if len(toks) > 1 else (
                ye if isinstance(ye, int) else None)
            changed = False
            if new_y != y:
                y = new_y
                changed = True
            if new_ye is not None and new_ye != ye:
                ye = new_ye
                changed = True
            if changed:
                if isinstance(ye, int) and y > ye:
                    y, ye = ye, y
                e["year"] = y
                e["yearEnd"] = ye
                e["dateText"] = f"{fmt(y)}－{fmt(ye)}" if ye != y else fmt(y)
                fixed_sign += 1

        # ---- B. 跨越事件上移到能容纳的父时期 ----
        if not isinstance(ye, int) or not isinstance(y, int):
            continue
        cur = by_id.get(e.get("periodId"))
        if cur is None:
            continue
        if span_ok(cur, y, ye):
            continue

        node = cur
        seen = set()
        target = None
        while node is not None and node["id"] not in seen:
            seen.add(node["id"])
            if span_ok(node, y, ye):
                target = node
                break
            pid = node.get("parentId")
            node = by_id.get(pid) if pid else None

        if target is not None and target["id"] != cur["id"]:
            e["periodId"] = target["id"]
            moved_up += 1
        elif target is None:
            # 兜底：没有任何时期能容纳完整跨度（例如「龙山文化」
            # 横跨新石器时代与夏的考古分界），把 yearEnd 钳到
            # 当前时期的末端，保留起点不变。
            cur2 = by_id.get(e.get("periodId"))
            if cur2 is not None and year_ok(cur2, y):
                e["yearEnd"] = min(ye, cur2["endYear"])
                if e["yearEnd"] != ye:
                    e["dateText"] = (f"{fmt(y)}－{fmt(e['yearEnd'])}"
                                     if e["yearEnd"] != y else fmt(y))
                    clamped += 1

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))

    print(f"{path}: sign-fixed {fixed_sign}, moved-to-ancestor {moved_up}, "
          f"clamped {clamped}, unresolved {len(unresolved)}")
    for u in unresolved[:12]:
        print(f"   unresolved {u[0]} [{u[1]}..{u[2]}] in {u[3]}")


if __name__ == "__main__":
    main()
