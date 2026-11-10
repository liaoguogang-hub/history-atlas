#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""历史图鉴 App 数据校验器。

用法:
    python tools/validate_data.py data/china.json data/world.json
    python tools/validate_data.py --strict data/*.json

校验项见 data/SCHEMA.md §8。退出码: 0 通过, 1 有 ERROR。
"""
import json
import sys
from pathlib import Path

# 权威定义见 data/SCHEMA.md §4 category 枚举，此处须保持同步
VALID_CATEGORIES = {
    "political", "military", "economic", "cultural", "scientific", "social",
    "religious", "art", "literature", "education", "technology", "exploration",
    "conflict", "treaty", "reform", "dynasty", "cross-civilization", "disaster",
    "health", "economy-crisis", "legend", "archaeology",
}

# 权威定义见 data/SCHEMA.md §5 colorKey 枚举
PERIOD_COLOR_KEYS = {
    "stone", "cyan", "zhou", "blue", "han", "green", "sui-tang", "yellow",
    "yuan", "pink", "qing", "gray", "modern", "purple",
    "prehistory", "mesopotamia", "india", "greece", "rome", "medieval",
    "renaissance", "earlymodern", "contemporary",
}

# 文本长度区间: (字段, 最小, 最大, 是否必填)
TEXT_RULES = [
    ("summary", 10, 120, True),
    ("detail", 80, 1200, False),
    ("biography", 100, 1400, False),
]


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def year_not_after(a, b):
    """a 是否不晚于 b。

    负数年份表示公元前，**数值越小时间越早**，因此统一用数值比较 a <= b：
      - 都为公元：a <= b
      - 都为公元前：a <= b（-3000000 早于 -2070；-520 早于 -456）
      - 跨公元：a < 0 <= b
    """
    if a >= 0 and b >= 0:
        return a <= b
    if a < 0 and b < 0:
        return a <= b
    return a < 0 <= b


def check_year_order(r, kind, start, end, label):
    """校验起止年份顺序。"""
    if is_int(start) and is_int(end) and not year_not_after(start, end):
        r.error(f"{label}: 起始年({start}) 晚于 结束年({end})")


def validate_file(path: Path, strict: bool = False) -> Report:
    r = Report()
    r.note(f"=== {path.name} ===")

    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        r.error("文件含 UTF-8 BOM, 应为无 BOM 的 UTF-8")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        r.error(f"非 UTF-8 编码: {e}")
        return r

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        r.error(f"JSON 解析失败: {e}")
        return r

    # ---- 顶层结构 ----
    if not isinstance(data, dict):
        r.error("顶层必须是 JSON 对象")
        return r

    for key in ("version", "scope", "periods", "events", "figures"):
        if key not in data:
            r.error(f"顶层缺少字段: {key}")

    scope = data.get("scope")
    if scope not in ("china", "world"):
        r.error(f"scope 非法: {scope!r} (应为 'china' 或 'world')")

    periods = data.get("periods") or []
    events = data.get("events") or []
    figures = data.get("figures") or []

    for name, arr in (("periods", periods), ("events", events), ("figures", figures)):
        if not isinstance(arr, list):
            r.error(f"{name} 必须是数组")
            return r

    if not periods:
        r.error("periods 为空")
    if not events:
        r.warn("events 为空")
    if not figures:
        r.warn("figures 为空")

    r.note(f"  periods={len(periods)}  events={len(events)}  figures={len(figures)}")

    # ---- id 唯一性 ----
    ids = {}
    for kind, arr in (("period", periods), ("event", events), ("figure", figures)):
        for i, item in enumerate(arr):
            if not isinstance(item, dict):
                r.error(f"{kind}[{i}] 不是对象")
                continue
            oid = item.get("id")
            if not oid or not isinstance(oid, str):
                r.error(f"{kind}[{i}] 缺少合法 id")
                continue
            if oid in ids:
                r.error(f"id 重复: '{oid}' ({ids[oid]} 与 {kind}[{i}])")
            else:
                ids[oid] = f"{kind}[{i}]"

    period_ids = {p.get("id") for p in periods if isinstance(p, dict)}
    event_ids = {e.get("id") for e in events if isinstance(e, dict)}
    figure_ids = {f.get("id") for f in figures if isinstance(f, dict)}

    # ---- periods ----
    period_by_id = {}
    for p in periods:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        period_by_id[pid] = p

        for req in ("name", "startYear", "endYear"):
            if req not in p:
                r.error(f"period '{pid}' 缺少字段 {req}")
        for opt in ("startDateText", "endDateText"):
            if opt not in p:
                r.warn(f"period '{pid}' 缺少展示字段 {opt}")

        sy, ey = p.get("startYear"), p.get("endYear")
        check_year_order(r, "period", sy, ey, f"period '{pid}' ({p.get('name')})")

        ck = p.get("colorKey")
        if ck and ck not in PERIOD_COLOR_KEYS:
            r.warn(f"period '{pid}' colorKey '{ck}' 不在推荐枚举内(将走 fallback)")

        parent = p.get("parentId")
        if parent is not None:
            if parent not in period_ids:
                r.error(f"period '{pid}' parentId '{parent}' 指向不存在的时期")
            elif parent == pid:
                r.error(f"period '{pid}' parentId 指向自身")
            else:
                # 子区间应落在父区间内
                pp = period_by_id.get(parent)
                if pp and is_int(sy) and is_int(ey) and is_int(pp.get("startYear")) and is_int(pp.get("endYear")):
                    if sy < pp["startYear"] or ey > pp["endYear"]:
                        r.warn(f"period '{pid}' 区间[{sy},{ey}]超出父 '{parent}' 区间[{pp['startYear']},{pp['endYear']}]")

        for fid in p.get("keyFigures") or []:
            if fid not in figure_ids:
                r.error(f"period '{pid}' keyFigures 引用不存在的人物 '{fid}'")
        for eid in p.get("relatedEvents") or []:
            if eid not in event_ids:
                r.error(f"period '{pid}' relatedEvents 引用不存在的事件 '{eid}'")

    # ---- events ----
    for e in events:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        for req in ("name", "year", "periodId", "category", "summary"):
            if req not in e:
                r.error(f"event '{eid}' 缺少字段 {req}")
        if "detail" not in e:
            r.warn(f"event '{eid}' 缺少 detail")

        y = e.get("year")
        ye = e.get("yearEnd")
        if y is not None and not is_int(y):
            r.error(f"event '{eid}' year 非整数: {y!r}")
        if ye is not None:
            if not is_int(ye):
                r.error(f"event '{eid}' yearEnd 非整数: {ye!r}")
            elif is_int(y) and not year_not_after(y, ye):
                r.error(f"event '{eid}' yearEnd({ye}) 早于 year({y})")

        cat = e.get("category")
        if cat not in VALID_CATEGORIES:
            r.error(f"event '{eid}' category 非法: {cat!r}")

        imp = e.get("importance")
        if imp is not None and imp not in (1, 2, 3, 4, 5):
            r.error(f"event '{eid}' importance 非法: {imp!r}")

        pid = e.get("periodId")
        if pid not in period_ids:
            r.error(f"event '{eid}' periodId '{pid}' 指向不存在的时期")
        else:
            p = period_by_id[pid]
            ps, pe = p.get("startYear"), p.get("endYear")
            if is_int(y) and is_int(ps) and is_int(pe):
                if not (year_not_after(ps, y) and year_not_after(y, pe)):
                    r.warn(f"event '{eid}' 年份 {y} 不在时期 '{pid}' 区间[{ps},{pe}]内")
                if is_int(ye) and not (year_not_after(ps, ye) and year_not_after(ye, pe)):
                    r.warn(f"event '{eid}' yearEnd {ye} 不在时期 '{pid}' 区间内")

        for fid in e.get("figures") or []:
            if fid not in figure_ids:
                r.error(f"event '{eid}' figures 引用不存在的人物 '{fid}'")

    # ---- figures ----
    for f in figures:
        if not isinstance(f, dict):
            continue
        fid = f.get("id")
        for req in ("name", "periodId", "role"):
            if req not in f:
                r.error(f"figure '{fid}' 缺少字段 {req}")

        by, dy = f.get("birthYear"), f.get("deathYear")
        if by is not None and not is_int(by):
            r.error(f"figure '{fid}' birthYear 非整数")
        if dy is not None and not is_int(dy):
            r.error(f"figure '{fid}' deathYear 非整数")
        # 负数年份表示公元前，数值越小时间越早。
        # 因此公元人物要求 by < dy，公元前人物（都为负）要求 by > dy。
        if is_int(by) and is_int(dy):
            if not year_not_after(by, dy):
                r.error(f"figure '{fid}' birthYear({by}) 晚于 deathYear({dy})")
        if by is not None and by == 0:
            r.warn(f"figure '{fid}' birthYear 为 0, 按约定不应使用 0 年")
        if dy is not None and dy == 0:
            r.warn(f"figure '{fid}' deathYear 为 0, 按约定不应使用 0 年")

        pid = f.get("periodId")
        if pid not in period_ids:
            r.error(f"figure '{fid}' periodId '{pid}' 指向不存在的时期")

        for eid in f.get("relatedEvents") or []:
            if eid not in event_ids:
                r.error(f"figure '{fid}' relatedEvents 引用不存在的事件 '{eid}'")
        for oid in f.get("relatedFigures") or []:
            if oid not in figure_ids:
                r.error(f"figure '{fid}' relatedFigures 引用不存在的人物 '{oid}'")

        g = f.get("gender")
        if g is not None and g not in ("male", "female", "unknown"):
            r.warn(f"figure '{fid}' gender 取值异常: {g!r}")

    # ---- 文本长度 ----
    # 契约 SCHEMA §2：period.summary 150–400 字；§3/§4：event.summary / figure.summary 40–120 字
    for arr, field, lo, hi, required in (
        (periods, "summary", 60, 400, True),
        (events, "summary", 10, 120, True),
        (figures, "summary", 10, 120, True),
    ):
        for item in arr:
            if not isinstance(item, dict):
                continue
            t = item.get(field)
            if t is None:
                if required:
                    r.error(f"{item.get('id')} 缺少 {field}")
                continue
            if not isinstance(t, str):
                r.error(f"{item.get('id')} {field} 不是字符串")
                continue
            if len(t) < lo:
                r.warn(f"{item.get('id')} {field} 过短({len(t)}字, 建议≥{lo})")
            elif len(t) > hi:
                r.warn(f"{item.get('id')} {field} 过长({len(t)}字, 建议≤{hi})")

    return r


def classify(msg):
    """把一条错误/警告归类，便于聚合统计。"""
    if "引用不存在的人物" in msg:
        return "missing_figure_ref"
    if "引用不存在的事件" in msg:
        return "missing_event_ref"
    if "引用不存在的时期" in msg:
        return "missing_period_ref"
    if "起始年" in msg or "晚于" in msg:
        return "year_order"
    if "不在时期" in msg:
        return "event_outside_period"
    if "id 重复" in msg:
        return "duplicate_id"
    if "category" in msg or "colorKey" in msg:
        return "enum_value"
    if "缺少" in msg or "必填" in msg or "为空" in msg:
        return "missing_field"
    if "过长" in msg or "过短" in msg:
        return "text_length"
    return "other"


def main(argv):
    strict = "--strict" in argv
    summary = "--summary" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print("用法: python tools/validate_data.py [--strict] [--summary] <file.json> [...]")
        return 2

    all_errors = 0
    all_warnings = 0
    for p in paths:
        if not p.exists():
            print(f"文件不存在: {p}")
            all_errors += 1
            continue
        r = validate_file(p, strict)
        for line in r.info:
            print(line)

        if summary:
            import collections
            ec = collections.Counter()
            wc = collections.Counter()
            ex = collections.defaultdict(list)
            for m in r.errors:
                k = classify(m)
                ec[k] += 1
                if len(ex[k]) < 3:
                    ex[k].append(m)
            for m in r.warnings:
                wc[classify(m)] += 1
            print("  -- 错误分类 --")
            for k, n in ec.most_common():
                print(f"    {n:5d}  {k}")
                for s in ex[k]:
                    print(f"           e.g. {s}")
            print("  -- 警告分类 --")
            for k, n in wc.most_common():
                print(f"    {n:5d}  {k}")
        else:
            for line in r.warnings[:40]:
                print(f"  [WARN] {line}")
            if len(r.warnings) > 40:
                print(f"  ... 另有 {len(r.warnings) - 40} 条警告")
            for line in r.errors[:40]:
                print(f"  [ERROR] {line}")
            if len(r.errors) > 40:
                print(f"  ... 另有 {len(r.errors) - 40} 条错误")

        all_errors += len(r.errors)
        all_warnings += len(r.warnings)
        print(f"  -> 错误 {len(r.errors)} / 警告 {len(r.warnings)}")

    print()
    print(f"汇总: 错误 {all_errors}, 警告 {all_warnings}")
    if all_errors:
        print("结论: 未通过")
        return 1
    if strict and all_warnings:
        print("结论: 严格模式，警告未清零 -> 未通过")
        return 1
    print("结论: 通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
