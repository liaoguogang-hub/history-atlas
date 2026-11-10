#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""历史图鉴 App 数据覆盖度分析。

用法:
    python tools/analyze_data.py data/china.json data/world.json

输出: 时期树结构、各时期事件/人物密度、按世纪的事件分布、
      事件类别占比、importance 分布、人物 role 分布、内容最薄的时期。
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fmt_year(y):
    if y is None:
        return "?"
    return f"前{-y}" if y < 0 else str(y)


def main(argv):
    if not argv:
        print("用法: python tools/analyze_data.py <file.json> [...]")
        return 2

    for path in argv:
        d = load(path)
        periods = d["periods"]
        events = d["events"]
        figures = d["figures"]

        print("=" * 78)
        print(f"{Path(path).name}  scope={d.get('scope')}  v{d.get('version')}")
        print("=" * 78)

        # ---- 时期树 ----
        by_id = {p["id"]: p for p in periods}
        kids = defaultdict(list)
        roots = []
        for p in periods:
            if p.get("parentId") and p["parentId"] in by_id:
                kids[p["parentId"]].append(p)
            else:
                roots.append(p)

        ev_by_period = Counter(e["periodId"] for e in events)
        fg_by_period = Counter(f["periodId"] for f in figures)

        print("\n【时期树】")
        for r in sorted(roots, key=lambda x: x.get("startYear") or 0):
            print(f"\n  ▣ {r['name']}  [{fmt_year(r.get('startYear'))} ~ {fmt_year(r.get('endYear'))}]"
                  f"  事件{ev_by_period.get(r['id'],0)} 人物{fg_by_period.get(r['id'],0)}"
                  f"  <{r.get('colorKey', '-')}>")
            for c in sorted(kids.get(r["id"], []), key=lambda x: x.get("startYear") or 0):
                print(f"      ├ {c['name']}  [{fmt_year(c.get('startYear'))} ~ {fmt_year(c.get('endYear'))}]"
                      f"  事件{ev_by_period.get(c['id'],0)} 人物{fg_by_period.get(c['id'],0)}")
                for g in sorted(kids.get(c["id"], []), key=lambda x: x.get("startYear") or 0):
                    print(f"      │   └ {g['name']}  [{fmt_year(g.get('startYear'))} ~ {fmt_year(g.get('endYear'))}]"
                          f"  事件{ev_by_period.get(g['id'],0)} 人物{fg_by_period.get(g['id'],0)}")

        # ---- 事件按世纪 ----
        print("\n【事件按世纪分布】")
        cent = Counter()
        for e in events:
            y = e.get("year")
            if y is None:
                continue
            if y < 0:
                cent[f"前{(abs(y) - 1) // 100 + 1}世纪"] += 1
            else:
                cent[f"{y // 100 + 1}世纪"] += 1

        def cent_key(c):
            if c.startswith("前"):
                return -(int(c[1:-2]) * 100)
            return int(c[:-2]) * 100

        for c in sorted(cent, key=cent_key):
            bar = "█" * max(1, cent[c] // 2)
            print(f"  {c:>8} {cent[c]:>5}  {bar}")

        # ---- 类别分布 ----
        print("\n【事件类别分布】")
        cats = Counter(e.get("category") for e in events)
        for c, n in cats.most_common():
            print(f"  {c:<22} {n:>5}")

        # ---- importance ----
        print("\n【事件重要度分布】")
        imps = Counter(e.get("importance") for e in events)
        for i in sorted(imps, key=lambda x: (x is None, x)):
            print(f"  {i} 星 {imps[i]:>5}  {'█' * min(60, imps[i] // 5)}")

        # ---- 人物 role ----
        print("\n【人物身份分布 Top 20】")
        roles = Counter(f.get("role") for f in figures)
        for role, n in roles.most_common(20):
            print(f"  {role:<18} {n:>5}")

        # ---- 内容最薄的时期 ----
        print("\n【内容最薄的时期（事件数 < 15）】")
        thin = [(p["name"], ev_by_period.get(p["id"], 0)) for p in periods
                if ev_by_period.get(p["id"], 0) < 15]
        if thin:
            for name, n in sorted(thin, key=lambda x: x[1]):
                print(f"  {name:<16} {n:>4} 事件")
        else:
            print("  无（所有时期均 ≥15 事件）")

        # ---- 人物无关联事件 ----
        orphan = [f["name"] for f in figures if not (f.get("relatedEvents") or [])]
        print(f"\n【人物未挂事件】 {len(orphan)} / {len(figures)}")
        if orphan[:12]:
            print(f"  例: {', '.join(orphan[:12])}")

        no_detail = [e["name"] for e in events if not (e.get("detail") or "").strip()]
        print(f"[事件缺 detail] {len(no_detail)} / {len(events)}")
        if no_detail[:10]:
            print(f"  例: {', '.join(no_detail[:10])}")

        print()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
