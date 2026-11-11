#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自然科学图鉴数据校验器（data-science/*.json）。

遵循 data/SCHEMA.md 数据契约 v1，但允许 scope 取 "physics" / "chem"。

用法:
    python tools/sci_content/validate_sci.py data-science/physics.json data-science/chemistry.json

校验项：
  - 顶层结构 version / scope / periods / events / figures
  - id 全局唯一、全小写 ASCII + 中划线、前缀正确
  - parentId / periodId / keyFigures / relatedEvents / relatedFigures / figures 引用无悬空
  - category 属于 SCHEMA §5 枚举
  - colorKey 属于 SCHEMA §6 枚举
  - importance ∈ {1..5}
  - startYear ≤ endYear、birthYear ≤ deathYear
  - 事件年份落在其 periodId 的区间内
  - period 树深度 ≤ 3，子区间完全落在父区间内
  - 文本长度：period.summary 150-400；event.summary 40-120；event.detail 150-800；
    figure.summary 40-120；figure.biography 200-1000
  - JSON 为 UTF-8 无 BOM

退出码: 0 全部 PASS，1 有 ERROR。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# 强制 UTF-8 输出，避免 Windows 控制台 GBK 编码导致中文乱码
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover
        pass

VALID_CATEGORIES = {
    "political", "military", "economic", "cultural", "scientific", "social",
    "religious", "art", "literature", "education", "technology", "exploration",
    "conflict", "treaty", "reform", "dynasty", "cross-civilization", "disaster",
    "health", "economy-crisis", "legend", "archaeology",
}

PERIOD_COLOR_KEYS = {
    "stone", "cyan", "zhou", "blue", "han", "green", "sui-tang", "yellow",
    "yuan", "pink", "qing", "gray", "modern", "purple",
    "prehistory", "mesopotamia", "india", "greece", "rome", "medieval",
    "renaissance", "earlymodern", "contemporary",
}

# data-science/SCHEMA.md §6：每个学科各自的色系
PHY_COLOR_KEYS = {
    "phy-classical", "phy-thermo", "phy-em", "phy-wave", "phy-quantum",
    "phy-relativity", "phy-nuclear", "phy-particle", "phy-condensed", "phy-astro",
}
CHEM_COLOR_KEYS = {
    "chem-alchemy", "chem-atomic", "chem-periodic", "chem-organic",
    "chem-electro", "chem-structure", "chem-bio", "chem-nuclear", "chem-material",
    "chem-industry",
}
COMMON_COLOR_KEYS = {"purple"}  # 跨尺度 / 专题

SCOPE_COLOR_KEYS = {
    "physics": PHY_COLOR_KEYS | COMMON_COLOR_KEYS,
    "chem": CHEM_COLOR_KEYS | COMMON_COLOR_KEYS,
}

# scope -> (period 前缀, event 前缀, figure 前缀)
SCOPE_PREFIX = {
    "physics": ("phy-", "ev-phy-", "fig-phy-"),
    "chem": ("chem-", "ev-chem-", "fig-chem-"),
}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

TEXT_RULES = [
    # (集合名, 字段, 最小, 最大)
    ("periods", "summary", 150, 400),
    ("events", "summary", 40, 120),
    ("events", "detail", 150, 800),
    ("figures", "summary", 40, 120),
    ("figures", "biography", 200, 1000),
]


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def year_ok(a: int, b: int) -> bool:
    """a 不晚于 b。负数=公元前，数值越小越早。"""
    if a >= 0 and b >= 0:
        return a <= b
    if a < 0 and b < 0:
        return a <= b
    return a < 0 <= b


def check_text(r: Report, kind: str, item: dict, field: str, lo: int, hi: int) -> None:
    t = item.get(field)
    iid = item.get("id")
    if not isinstance(t, str):
        r.error(f"{kind} '{iid}' 缺少或非法字段 {field}")
        return
    n = len(t)
    if n < lo:
        r.error(f"{kind} '{iid}' {field} 过短({n}字, 要求 {lo}-{hi})")
    elif n > hi:
        r.error(f"{kind} '{iid}' {field} 过长({n}字, 要求 {lo}-{hi})")


def validate_file(path: Path) -> Report:
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

    if not isinstance(data, dict):
        r.error("顶层必须是 JSON 对象")
        return r

    for key in ("version", "scope", "periods", "events", "figures"):
        if key not in data:
            r.error(f"顶层缺少字段: {key}")

    if data.get("version") != 1:
        r.error(f"version 必须为 1, 实际 {data.get('version')!r}")

    scope = data.get("scope")
    if scope not in SCOPE_PREFIX:
        r.error(f"scope 非法: {scope!r} (应为 'physics' 或 'chem')")
        return r
    pfx, ev_pfx, fig_pfx = SCOPE_PREFIX[scope]

    periods = data.get("periods") or []
    events = data.get("events") or []
    figures = data.get("figures") or []
    for name, arr in (("periods", periods), ("events", events), ("figures", figures)):
        if not isinstance(arr, list):
            r.error(f"{name} 必须是数组")
            return r
        if not arr:
            r.error(f"{name} 为空")

    r.note(f"  scope={scope}  periods={len(periods)}  events={len(events)}  figures={len(figures)}")

    # ---- id 唯一性与格式 ----
    ids: dict[str, str] = {}
    for kind, arr, want in (("period", periods, pfx), ("event", events, ev_pfx),
                             ("figure", figures, fig_pfx)):
        for i, item in enumerate(arr):
            if not isinstance(item, dict):
                r.error(f"{kind}[{i}] 不是对象")
                continue
            oid = item.get("id")
            if not isinstance(oid, str) or not oid:
                r.error(f"{kind}[{i}] 缺少合法 id")
                continue
            if oid in ids:
                r.error(f"id 重复: '{oid}' ({ids[oid]} 与 {kind}[{i}])")
            else:
                ids[oid] = f"{kind}[{i}]"
            if not ID_RE.match(oid):
                r.error(f"{kind} '{oid}' id 不符合「全小写 ASCII + 中划线」")
            if not oid.startswith(want):
                r.error(f"{kind} '{oid}' id 前缀应为 '{want}'")

    period_ids = {p["id"] for p in periods if isinstance(p, dict) and isinstance(p.get("id"), str)}
    event_ids = {e["id"] for e in events if isinstance(e, dict) and isinstance(e.get("id"), str)}
    figure_ids = {f["id"] for f in figures if isinstance(f, dict) and isinstance(f.get("id"), str)}
    period_by_id = {p["id"]: p for p in periods if isinstance(p, dict) and isinstance(p.get("id"), str)}

    # ---- periods ----
    for p in periods:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        for req in ("name", "startYear", "endYear", "summary", "startDateText", "endDateText"):
            if req not in p:
                r.error(f"period '{pid}' 缺少字段 {req}")
        if "parentId" not in p:
            r.error(f"period '{pid}' 缺少字段 parentId")

        sy, ey = p.get("startYear"), p.get("endYear")
        if is_int(sy) and is_int(ey) and not year_ok(sy, ey):
            r.error(f"period '{pid}' 起始年({sy}) 晚于 结束年({ey})")
        if sy == 0 or ey == 0:
            r.error(f"period '{pid}' 年份为 0, 按约定不使用 0 年")

        ck = p.get("colorKey")
        if ck and ck not in SCOPE_COLOR_KEYS[scope]:
            r.error(f"period '{pid}' colorKey '{ck}' 不在本学科（{scope}）的 §6 配色键枚举内")

        parent = p.get("parentId")
        if parent is not None:
            if parent not in period_ids:
                r.error(f"period '{pid}' parentId '{parent}' 指向不存在的时期")
            elif parent == pid:
                r.error(f"period '{pid}' parentId 指向自身")
            else:
                pp = period_by_id.get(parent)
                if pp and all(is_int(x) for x in (sy, ey, pp.get("startYear"), pp.get("endYear"))):
                    if sy < pp["startYear"] or ey > pp["endYear"]:
                        r.error(
                            f"period '{pid}' 区间[{sy},{ey}]未落在父 '{parent}' "
                            f"区间[{pp['startYear']},{pp['endYear']}]内"
                        )

        for fid in p.get("keyFigures") or []:
            if fid not in figure_ids:
                r.error(f"period '{pid}' keyFigures 引用不存在的人物 '{fid}'")
        for eid in p.get("relatedEvents") or []:
            if eid not in event_ids:
                r.error(f"period '{pid}' relatedEvents 引用不存在的事件 '{eid}'")

        # 顶层分期必须带「编年主干」标签
        if p.get("parentId") is None and "编年主干" not in (p.get("tags") or []):
            r.error(f"顶层 period '{pid}' 的 tags 缺少「编年主干」")

    # ---- period 树深度 ----
    def depth(pid, seen=None):
        seen = seen or set()
        if pid in seen:
            return 99
        seen = seen | {pid}
        par = period_by_id.get(pid, {}).get("parentId")
        if not par:
            return 1
        return 1 + depth(par, seen)

    for pid in period_ids:
        d = depth(pid)
        if d > 3:
            r.error(f"period '{pid}' 树深度为 {d}, 超过 3 层")

    # ---- events ----
    for e in events:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        for req in ("name", "year", "periodId", "category", "summary", "detail", "dateText"):
            if req not in e:
                r.error(f"event '{eid}' 缺少字段 {req}")

        y, ye = e.get("year"), e.get("yearEnd")
        if not is_int(y):
            r.error(f"event '{eid}' year 非整数")
        if ye is not None:
            if not is_int(ye):
                r.error(f"event '{eid}' yearEnd 非整数")
            elif is_int(y) and not year_ok(y, ye):
                r.error(f"event '{eid}' yearEnd({ye}) 早于 year({y})")
        if y == 0:
            r.error(f"event '{eid}' year 为 0, 按约定不使用 0 年")

        cat = e.get("category")
        if cat not in VALID_CATEGORIES:
            r.error(f"event '{eid}' category 非法: {cat!r}")

        imp = e.get("importance")
        if imp not in (1, 2, 3, 4, 5):
            r.error(f"event '{eid}' importance 非法: {imp!r}")

        pid = e.get("periodId")
        if pid not in period_ids:
            r.error(f"event '{eid}' periodId '{pid}' 指向不存在的时期")
        else:
            p = period_by_id[pid]
            ps, pe = p.get("startYear"), p.get("endYear")
            if all(is_int(x) for x in (y, ps, pe)):
                if not (year_ok(ps, y) and year_ok(y, pe)):
                    r.error(f"event '{eid}' 年份 {y} 不在时期 '{pid}' 区间[{ps},{pe}]内")
            if is_int(ye) and all(is_int(x) for x in (ye, ps, pe)):
                if not (year_ok(ps, ye) and year_ok(ye, pe)):
                    r.error(f"event '{eid}' yearEnd {ye} 不在时期 '{pid}' 区间[{ps},{pe}]内")

        for fid in e.get("figures") or []:
            if fid not in figure_ids:
                r.error(f"event '{eid}' figures 引用不存在的人物 '{fid}'")

    # ---- figures ----
    for f in figures:
        if not isinstance(f, dict):
            continue
        fid = f.get("id")
        for req in ("name", "periodId", "role", "lifeText", "summary", "biography"):
            if req not in f:
                r.error(f"figure '{fid}' 缺少字段 {req}")

        by, dy = f.get("birthYear"), f.get("deathYear")
        if by is not None and not is_int(by):
            r.error(f"figure '{fid}' birthYear 非整数")
        if dy is not None and not is_int(dy):
            r.error(f"figure '{fid}' deathYear 非整数")
        if is_int(by) and is_int(dy) and not year_ok(by, dy):
            r.error(f"figure '{fid}' birthYear({by}) 晚于 deathYear({dy})")
        if by == 0 or dy == 0:
            r.error(f"figure '{fid}' 年份为 0, 按约定不使用 0 年")

        pid = f.get("periodId")
        if pid not in period_ids:
            r.error(f"figure '{fid}' periodId '{pid}' 指向不存在的时期")

        g = f.get("gender")
        if g is not None and g not in ("male", "female", "unknown"):
            r.error(f"figure '{fid}' gender 取值异常: {g!r}")

        for eid in f.get("relatedEvents") or []:
            if eid not in event_ids:
                r.error(f"figure '{fid}' relatedEvents 引用不存在的事件 '{eid}'")
        for oid in f.get("relatedFigures") or []:
            if oid not in figure_ids:
                r.error(f"figure '{fid}' relatedFigures 引用不存在的人物 '{oid}'")

        ach = f.get("achievements")
        if ach is not None:
            if not isinstance(ach, list):
                r.error(f"figure '{fid}' achievements 不是数组")
            elif not (3 <= len(ach) <= 6):
                r.error(f"figure '{fid}' achievements 条目数 {len(ach)}, 要求 3-6")
        q = f.get("quotes")
        if q is not None:
            if not isinstance(q, list):
                r.error(f"figure '{fid}' quotes 不是数组")
            elif len(q) > 3:
                r.error(f"figure '{fid}' quotes 条目数 {len(q)}, 最多 3")

    # ---- 文本长度 ----
    for arr, field, lo, hi in TEXT_RULES:
        for item in arr:
            if isinstance(item, dict):
                check_text(r, arr is periods and "period" or (arr is events and "event" or "figure"),
                           item, field, lo, hi)

    return r


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print("用法: python tools/sci_content/validate_sci.py <file.json> [...]")
        return 2

    total_errors = 0
    total_warnings = 0
    for p in paths:
        if not p.exists():
            print(f"文件不存在: {p}")
            total_errors += 1
            continue
        r = validate_file(p)
        for line in r.notes:
            print(line)
        for line in r.warnings[:30]:
            print(f"  [WARN] {line}")
        for line in r.errors[:60]:
            print(f"  [ERROR] {line}")
        if len(r.errors) > 60:
            print(f"  ... 另有 {len(r.errors) - 60} 条错误")
        total_errors += len(r.errors)
        total_warnings += len(r.warnings)
        status = "PASS" if not r.errors else "FAIL"
        print(f"  -> {status}  错误 {len(r.errors)} / 警告 {len(r.warnings)}")
        print()

    print(f"汇总: 错误 {total_errors}, 警告 {total_warnings}")
    if total_errors:
        print("结论: 未通过")
        return 1
    print("结论: 全部 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
