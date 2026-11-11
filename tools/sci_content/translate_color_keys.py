#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
把 data-science/*.json 里的 colorKey 从「通用历史色」翻译为「学科专属色」。

背景
----
内容生成方最初沿用了 history-atlas 的通用色名（stone / cyan / yellow / gray …）。
那些键在科学图鉴的调色板里不存在，App 会走哈希回退调色板——
颜色稳定但**不带学科语义**，四个学科看上去就没有区别。

本脚本按分期名与学科语义做一次确定性映射，落到科学图鉴的四套学科色系上：

    geo-    地理    大地 / 海洋 / 冰川
    astro-  天文    深空 / 太阳 / 星系
    phy-    物理    力学 / 电磁 / 量子
    chem-   化学    炼金 / 原子 / 周期表

映射规则（按优先级，先命中先用）
--------------------------------
1. 名称含明确语义关键词（如「板块」「海洋」「量子」「周期表」）→ 直接命中学科色。
2. 否则按分期的年代定位到该学科色系里的一档（深→浅随时代推进）。
3. `purple` 保持不变 —— 它是「跨尺度 / 专题」的契约保留键。

脚本是幂等的：已翻译过的键（以学科前缀开头）不会被二次翻译。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA_DIR = os.path.join(ROOT, "data-science")

# ---------------------------------------------------------------------------
# 语义关键词 → 学科色键
# 关键词按「先命中先用」排列，因此更具体的词放前面。
# ---------------------------------------------------------------------------
KEYWORD_MAP = {
    # ---- 地理 ----
    "地质": "geo-deep", "深时": "geo-deep", "构造": "geo-deep", "板块": "geo-deep",
    "漂移": "geo-deep", "岩石": "geo-deep", "矿物": "geo-deep",
    "海洋": "geo-ocean", "洋中脊": "geo-ocean", "海底": "geo-ocean",
    "海岸": "geo-coast", "滩": "geo-coast",
    "河": "geo-river", "水系": "geo-river", "湖": "geo-river",
    "沙漠": "geo-desert", "荒漠": "geo-desert", "干旱": "geo-desert",
    "冰": "geo-polar", "极地": "geo-polar", "冰川": "geo-polar",
    "山": "geo-mountain", "高原": "geo-mountain", "地形": "geo-mountain",
    "火山": "geo-volcano", "地震": "geo-volcano",
    "喀斯特": "geo-karst", "溶洞": "geo-karst",
    "平原": "geo-plain", "沙漠化": "geo-plain",

    # ---- 天文 ----
    "太阳": "astro-solar", "行星": "astro-planet", "地球": "astro-planet",
    "火星": "astro-planet", "金星": "astro-planet", "木星": "astro-planet",
    "土星": "astro-planet", "彗星": "astro-comet", "小行星": "astro-comet",
    "流星": "astro-comet", "卫星": "astro-comet",
    "星系": "astro-galaxy", "银河": "astro-galaxy", "星系团": "astro-galaxy",
    "宇宙学": "astro-cosmo", "大爆炸": "astro-cosmo", "暴胀": "astro-cosmo",
    "星云": "astro-galaxy", "恒星": "astro-galaxy", "黑洞": "astro-cosmo",
    "观测": "astro-telescope", "望远镜": "astro-telescope", "光谱": "astro-telescope",
    "射电": "astro-telescope", "空间": "astro-telescope",
    "量子": "astro-quanta", "辐射": "astro-quanta", "光子": "astro-quanta",

    # ---- 物理 ----
    "经典力学": "phy-classical", "力学": "phy-classical", "牛顿": "phy-classical",
    "热学": "phy-thermo", "统计物理": "phy-thermo", "热力学": "phy-thermo",
    "电磁": "phy-em", "电学": "phy-em", "磁": "phy-em",
    "量子力学": "phy-quantum", "量子场论": "phy-particle",
    "粒子": "phy-particle", "标准模型": "phy-particle", "夸克": "phy-particle",
    "核": "phy-nuclear", "裂变": "phy-nuclear", "聚变": "phy-nuclear",
    "凝聚态": "phy-condensed", "固体": "phy-condensed", "超导": "phy-condensed",
    "相对论": "phy-relativity", "时空": "phy-relativity", "引力波": "phy-relativity",
    "波动": "phy-wave", "声": "phy-wave", "光": "phy-wave", "振动": "phy-wave",
    "弦": "phy-astro", "超弦": "phy-astro", "理论物理": "phy-astro",

    # ---- 化学 ----
    "炼金": "chem-alchemy", "早期化学": "chem-alchemy",
    "原子论": "chem-atomic", "原子": "chem-atomic",
    "周期表": "chem-periodic", "元素周期": "chem-periodic", "周期律": "chem-periodic",
    "有机": "chem-organic", "碳": "chem-organic", "聚合物": "chem-organic",
    "电化学": "chem-electro", "电池": "chem-electro", "电解": "chem-electro",
    "结构化学": "chem-structure", "晶体": "chem-structure", "分子结构": "chem-structure",
    "生物化学": "chem-bio", "蛋白": "chem-bio", "核酸": "chem-bio", "酶": "chem-bio",
    "核化学": "chem-nuclear", "放射性": "chem-nuclear", "同位素": "chem-nuclear",
    "材料": "chem-material", "高分子": "chem-material", "陶瓷": "chem-material",
    "工业化学": "chem-industry", "化工": "chem-industry", "催化": "chem-industry",
}

# 各学科色系：按年代从早到晚排，用于兜底的时间定位。
SCOPE_RAMP = {
    "geo": ["geo-deep", "geo-river", "geo-plain", "geo-coast", "geo-mountain", "geo-polar"],
    "astro": ["astro-deep", "astro-solar", "astro-planet", "astro-comet",
              "astro-galaxy", "astro-telescope", "astro-quanta", "astro-cosmo"],
    "physics": ["phy-classical", "phy-thermo", "phy-em", "phy-wave",
                "phy-relativity", "phy-quantum", "phy-nuclear", "phy-particle",
                "phy-condensed", "phy-astro"],
    "chem": ["chem-alchemy", "chem-atomic", "chem-periodic", "chem-electro",
             "chem-organic", "chem-structure", "chem-bio", "chem-nuclear",
             "chem-material", "chem-industry"],
}

# 已经是科学图鉴调色板里的键，不动。
KNOWN_PREFIXES = ("geo-", "astro-", "phy-", "chem-")
RESERVED = {"purple"}

# 通用历史色 → 语义兜底（当名称里找不到关键词时，用它来决定大致色系位置）
LEGACY_FALLBACK = {
    "stone": "geo-deep", "cyan": "geo-river", "blue": "astro-deep",
    "green": "geo-plain", "yellow": "chem-periodic", "pink": "chem-organic",
    "purple": "purple", "gray": "astro-deep", "modern": "phy-quantum",
    "prehistory": "geo-deep", "mesopotamia": "chem-alchemy",
    "india": "chem-alchemy", "greece": "phy-classical", "rome": "chem-alchemy",
    "medieval": "chem-alchemy", "renaissance": "phy-classical",
    "earlymodern": "phy-em", "contemporary": "phy-quantum",
}


def scope_of(data, filename):
    """从 scope 字段取学科；取不到则从文件名推断。"""
    scope = (data.get("scope") or "").strip().lower()
    if scope in SCOPE_RAMP:
        return scope
    stem = os.path.splitext(os.path.basename(filename))[0].lower()
    return stem if stem in SCOPE_RAMP else "geo"


def pick_by_keywords(text, scope):
    """名称/别名/标签里找语义关键词。命中返回色键，否则返回 None。"""
    haystack = " ".join(
        str(x) for x in (text.get("name", ""), text.get("alias", ""),
                         " ".join(text.get("tags", []) or []),
                         text.get("culture", ""), text.get("summary", "")[:120])
        if x
    )
    for kw, key in KEYWORD_MAP.items():
        if kw in haystack and key.startswith(scope + "-"):
            return key
    # 关键词命中但属于别的学科时，忽略（避免跨学科串色）
    return None


def pick_by_year(period, scope, siblings):
    """按年代在学科色系里定位一档。

    用**排名**而不是比例来分配：比例法会让大量集中在同一时代簇的分期
    挤到同一档（例如物理学里十几个 20 世纪分期全落到 `phy-condensed`）。
    排名法把同代分期依次摊到相邻色档上，视觉上更均匀。
    """
    ramp = SCOPE_RAMP[scope]
    lo_all = min((min(p.get("startYear", 0), p.get("endYear", 0)) for p in siblings),
                 default=0)
    hi_all = max((max(p.get("startYear", 0), p.get("endYear", 0)) for p in siblings),
                 default=0)
    if hi_all <= lo_all:
        return ramp[0]

    # 同一代（起始年落在同一档区间）的分期，按 id 排序后依次取相邻色档
    buckets = {}
    for p in siblings:
        lo = min(p.get("startYear", 0), p.get("endYear", 0))
        ratio = (lo - lo_all) / float(hi_all - lo_all)
        b = int(ratio * (len(ramp) - 1))
        buckets.setdefault(b, []).append(p)
    for b in buckets:
        buckets[b].sort(key=lambda p: (p.get("startYear", 0), p.get("id", "")))

    lo = min(period.get("startYear", 0), period.get("endYear", 0))
    ratio = (lo - lo_all) / float(hi_all - lo_all)
    bucket = int(ratio * (len(ramp) - 1))
    bucket = max(0, min(bucket, len(ramp) - 1))
    same = buckets.get(bucket, [])
    try:
        pos = next(i for i, p in enumerate(same) if p.get("id") == period.get("id"))
    except StopIteration:
        pos = 0
    # 同代内依次错开，步长取色档数的约数避免撞色
    step = max(1, len(ramp) // max(1, len(same)))
    idx = (bucket + pos * step) % len(ramp)
    return ramp[idx]


def translate(data, filename):
    scope = scope_of(data, filename)
    periods = data.get("periods", [])
    changed = []
    for p in periods:
        key = (p.get("colorKey") or "").strip().lower()
        # 已经翻译过 / 保留键 → 跳过
        if key in RESERVED or key.startswith(KNOWN_PREFIXES):
            continue

        new_key = pick_by_keywords(p, scope)
        if new_key is None:
            legacy = LEGACY_FALLBACK.get(key)
            if legacy and legacy.startswith(scope + "-"):
                new_key = legacy
            elif legacy == "purple":
                new_key = "purple"
            else:
                new_key = pick_by_year(p, scope, periods)

        changed.append((p.get("name"), key, new_key))
        p["colorKey"] = new_key
    return scope, changed


def main():
    files = sys.argv[1:] or [
        os.path.join(DATA_DIR, n)
        for n in ("geo.json", "astro.json", "physics.json", "chem.json")
    ]
    for path in files:
        if not os.path.isfile(path):
            print(f"[skip] 文件不存在：{path}")
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        scope, changed = translate(data, path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"=== {os.path.basename(path)}（scope={scope}）翻译 {len(changed)} 个 colorKey ===")
        for name, old, new in changed:
            print(f"  {name}: {old or '(空)'} -> {new}")


if __name__ == "__main__":
    main()
