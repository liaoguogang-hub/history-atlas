#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自然科学数据文件校验器（SCHEMA v1 扩展，支持多学科 scope）。

用法:
    python tools/sci_content/validate_geo_astro.py data-science/geo.json data-science/astro.json

说明:
    本脚本与 tools/sci_content/validate_sci.py 并存, 后者由物理/化学学科使用。
    两者互不覆盖: 本脚本只做只读校验, 不写入任何文件。

校验项:
  - 顶层字段、version=1、scope 合法
  - id 全局唯一 + 小写 ASCII + 中划线 + 学科前缀
  - periodId / parentId / keyFigures / relatedEvents / relatedFigures / figures 引用无悬空
  - period 树深度 <= 3，无环
  - 子 period 年份区间完全落在父 period 区间内
  - event / figure 的 periodId 存在，且事件年份落在所属 period 区间内
  - category 属于 SCHEMA §5 枚举
  - colorKey 属于 SCHEMA §6 枚举
  - importance ∈ {1..5}
  - 年份顺序（start<=end, birth<=death），不使用 0 年
  - UTF-8 无 BOM
  - 文本长度（period.summary 150-400；event.summary 40-120 / detail 150-800；
    figure.summary 40-120 / biography 200-1000 / achievements 3-6 / quotes 0-3）

退出码: 0 全部 PASS, 1 有 ERROR。
"""
import json
import sys
from pathlib import Path

VALID_CATEGORIES = {
    "political", "military", "economic", "cultural", "scientific", "social",
    "religious", "art", "literature", "education", "technology", "exploration",
    "conflict", "treaty", "reform", "dynasty", "cross-civilization", "disaster",
    "health", "economy-crisis", "legend", "archaeology",
}

PERIOD_COLOR_KEYS = {
    # history-atlas 通用键（data/SCHEMA.md §6）
    "stone", "cyan", "zhou", "blue", "han", "green", "sui-tang", "yellow",
    "yuan", "pink", "qing", "gray", "modern", "purple",
    "prehistory", "mesopotamia", "india", "greece", "rome", "medieval",
    "renaissance", "earlymodern", "contemporary",
    # 自然科学学科色系（data-science/SCHEMA.md §6）
    "geo-deep", "geo-river", "geo-coast", "geo-ocean", "geo-plain",
    "geo-volcano", "geo-mountain", "geo-karst", "geo-desert", "geo-polar",
    "astro-deep", "astro-galaxy", "astro-solar", "astro-telescope",
    "astro-planet", "astro-quanta", "astro-comet", "astro-cosmo",
    "phy-classical", "phy-particle", "phy-thermo", "phy-relativity",
    "phy-em", "phy-wave", "phy-quantum", "phy-astro", "phy-nuclear",
    "phy-condensed",
    "chem-alchemy", "chem-structure", "chem-atomic", "chem-bio",
    "chem-periodic", "chem-nuclear", "chem-organic", "chem-material",
    "chem-electro", "chem-industry",
}

ALLOWED_SCOPES = {"geo", "astro", "physics", "chem"}

# 学科类事件推荐分类
PREFERRED_CATEGORIES = {
    "scientific", "technology", "exploration", "reform", "cultural",
    "economic", "treaty", "disaster", "health", "education", "political",
    "archaeology", "cross-civilization", "legend",
}

# scope -> (period 前缀, event 前缀, figure 前缀)
PREFIXES = {
    "geo": ("geo-", "ev-geo-", "fig-geo-"),
    "astro": ("astro-", "ev-astro-", "fig-astro-"),
    "physics": ("phy-", "ev-phy-", "fig-phy-"),
    "chem": ("chem-", "ev-chem-", "fig-chem-"),
}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.notes.append(m)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def year_not_after(a, b):
    """负数=公元前；数值越小越早。a 不晚于 b。"""
    if a >= 0 and b >= 0:
        return a <= b
    if a < 0 and b < 0:
        return a <= b
    return a < 0 <= b


def check_text(r, kind, item_id, field, lo, hi, required=True, item=None):
    t = item.get(field)
    if t is None:
        if required:
            r.error(f"{kind} '{item_id}' 缺少 {field}")
        return
    if not isinstance(t, str):
        r.error(f"{kind} '{item_id}' {field} 不是字符串")
        return
    n = len(t)
    if n < lo:
        r.error(f"{kind} '{item_id}' {field} 过短({n}字, 要求 {lo}-{hi})")
    elif n > hi:
        r.error(f"{kind} '{item_id}' {field} 过长({n}字, 要求 {lo}-{hi})")


def validate(path: Path) -> Report:
    r = Report()
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
    if scope not in ALLOWED_SCOPES:
        r.error(f"scope 非法: {scope!r} (应为 {sorted(ALLOWED_SCOPES)})")
        scope = None

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
        r.error("events 为空")
    if not figures:
        r.error("figures 为空")

    r.note(f"periods={len(periods)} events={len(events)} figures={len(figures)}")

    # ---- id 唯一性 + 前缀 + 命名规范 ----
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
            if scope and scope in PREFIXES:
                pp, ep, fp = PREFIXES[scope]
                if kind == "period" and not oid.startswith(pp):
                    r.error(f"period '{oid}' id 前缀应为 '{pp}'")
                if kind == "event" and not oid.startswith(ep):
                    r.error(f"event '{oid}' id 前缀应为 '{ep}'")
                if kind == "figure" and not oid.startswith(fp):
                    r.error(f"figure '{oid}' id 前缀应为 '{fp}'")
            if oid != oid.lower() or not all(c.isalnum() or c == "-" for c in oid):
                r.error(f"{kind} '{oid}' id 必须全小写 ASCII + 中划线")

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
        for req in ("name", "startYear", "endYear", "startDateText", "endDateText", "summary"):
            if req not in p:
                r.error(f"period '{pid}' 缺少字段 {req}")
        sy, ey = p.get("startYear"), p.get("endYear")
        if not is_int(sy) or not is_int(ey):
            r.error(f"period '{pid}' startYear/endYear 必须为整数")
        elif not year_not_after(sy, ey):
            r.error(f"period '{pid}' 起始年({sy}) 晚于结束年({ey})")
        ck = p.get("colorKey")
        if ck and ck not in PERIOD_COLOR_KEYS:
            r.error(f"period '{pid}' colorKey '{ck}' 不在 §6 枚举内")
        parent = p.get("parentId")
        if parent is not None:
            if parent not in period_ids:
                r.error(f"period '{pid}' parentId '{parent}' 指向不存在的时期")
            elif parent == pid:
                r.error(f"period '{pid}' parentId 指向自身")
            else:
                pp = period_by_id.get(parent)
                if pp and is_int(sy) and is_int(ey) and is_int(pp.get("startYear")) and is_int(pp.get("endYear")):
                    if sy < pp["startYear"] or ey > pp["endYear"]:
                        r.error(
                            f"period '{pid}' 区间[{sy},{ey}]超出父 '{parent}' 区间"
                            f"[{pp['startYear']},{pp['endYear']}]"
                        )
        for fid in p.get("keyFigures") or []:
            if fid not in figure_ids:
                r.error(f"period '{pid}' keyFigures 引用不存在的人物 '{fid}'")
        for eid in p.get("relatedEvents") or []:
            if eid not in event_ids:
                r.error(f"period '{pid}' relatedEvents 引用不存在的事件 '{eid}'")
        check_text(r, "period", pid, "summary", 150, 400, item=p)

    # ---- period 树深度 & 环 ----
    def depth(pid, seen):
        if pid in seen:
            r.error(f"period 树出现环: {' -> '.join(seen + [pid])}")
            return 99
        p = period_by_id.get(pid)
        if not p:
            return 0
        parent = p.get("parentId")
        if parent is None:
            return 1
        return 1 + depth(parent, seen + [pid])

    for pid in period_ids:
        d = depth(pid, [])
        if d > 3:
            r.error(f"period '{pid}' 树深度 {d} > 3")

    # ---- events ----
    for e in events:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        for req in ("name", "year", "periodId", "category", "summary", "detail", "dateText"):
            if req not in e:
                r.error(f"event '{eid}' 缺少字段 {req}")
        y, ye = e.get("year"), e.get("yearEnd")
        if y is not None and not is_int(y):
            r.error(f"event '{eid}' year 非整数: {y!r}")
        if ye is not None:
            if not is_int(ye):
                r.error(f"event '{eid}' yearEnd 非整数: {ye!r}")
            elif is_int(y) and not year_not_after(y, ye):
                r.error(f"event '{eid}' yearEnd({ye}) 早于 year({y})")
        if y == 0:
            r.error(f"event '{eid}' year 为 0, 按约定不应使用 0 年")
        cat = e.get("category")
        if cat not in VALID_CATEGORIES:
            r.error(f"event '{eid}' category 非法: {cat!r}")
        elif cat not in PREFERRED_CATEGORIES:
            r.warn(f"event '{eid}' category '{cat}' 不在学科推荐集合内")
        imp = e.get("importance")
        if imp not in (1, 2, 3, 4, 5):
            r.error(f"event '{eid}' importance 非法: {imp!r}")
        pid = e.get("periodId")
        if pid not in period_ids:
            r.error(f"event '{eid}' periodId '{pid}' 指向不存在的时期")
        else:
            p = period_by_id[pid]
            ps, pe = p.get("startYear"), p.get("endYear")
            if is_int(y) and is_int(ps) and is_int(pe):
                if not (year_not_after(ps, y) and year_not_after(y, pe)):
                    r.error(f"event '{eid}' 年份 {y} 不在时期 '{pid}' 区间[{ps},{pe}]内")
                if is_int(ye) and not (year_not_after(ps, ye) and year_not_after(ye, pe)):
                    r.error(f"event '{eid}' yearEnd {ye} 不在时期 '{pid}' 区间内")
        for fid in e.get("figures") or []:
            if fid not in figure_ids:
                r.error(f"event '{eid}' figures 引用不存在的人物 '{fid}'")
        check_text(r, "event", eid, "summary", 40, 120, item=e)
        check_text(r, "event", eid, "detail", 150, 800, item=e)

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
        if by == 0 or dy == 0:
            r.error(f"figure '{fid}' 生卒年不应为 0")
        if is_int(by) and is_int(dy) and not year_not_after(by, dy):
            r.error(f"figure '{fid}' birthYear({by}) 晚于 deathYear({dy})")
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
            r.error(f"figure '{fid}' gender 取值异常: {g!r}")
        check_text(r, "figure", fid, "summary", 40, 120, item=f)
        check_text(r, "figure", fid, "biography", 200, 1000, item=f)
        ach = f.get("achievements") or []
        if not isinstance(ach, list):
            r.error(f"figure '{fid}' achievements 必须是数组")
        elif not (3 <= len(ach) <= 6):
            r.error(f"figure '{fid}' achievements 条目数 {len(ach)}, 要求 3-6")
        q = f.get("quotes") or []
        if not isinstance(q, list):
            r.error(f"figure '{fid}' quotes 必须是数组")
        elif len(q) > 3:
            r.error(f"figure '{fid}' quotes 条目数 {len(q)}, 要求 0-3")

    return r


def main(argv):
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print("用法: python tools/sci_content/validate_geo_astro.py <file.json> [...]")
        return 2

    total_err = 0
    total_warn = 0
    for p in paths:
        print(f"=== {p.name} ===")
        if not p.exists():
            print(f"  [ERROR] 文件不存在: {p}")
            total_err += 1
            continue
        r = validate(p)
        for n in r.notes:
            print(f"  {n}")
        for m in r.errors:
            print(f"  [ERROR] {m}")
        for m in r.warnings:
            print(f"  [WARN] {m}")
        total_err += len(r.errors)
        total_warn += len(r.warnings)
        if not r.errors and not r.warnings:
            print("  PASS")
        elif not r.errors:
            print(f"  PASS (有 {len(r.warnings)} 条建议级警告)")
        print()

    print("=" * 50)
    if total_err:
        print(f"结论: 未通过  错误 {total_err} / 警告 {total_warn}")
        return 1
    print(f"结论: 全部 PASS  错误 0 / 警告 {total_warn}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
