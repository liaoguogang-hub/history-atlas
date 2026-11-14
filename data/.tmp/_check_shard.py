# -*- coding: utf-8 -*-
"""通用校验器：检查待合入的世界史分片是否合规。

检查项：
  1. id 冲突（与现有 events/figures）
  2. 事件 year~yearEnd 是否落在 periodId 区间内
  3. 人物 birthYear/deathYear 是否落在 periodId 区间内（含跨度容差）
  4. 引用是否全部存在（figures / relatedEvents / relatedFigures）

用法：
    python data/.tmp/_check_shard.py data/.tmp/world_events_zzbq15.json [...]
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load_world():
    return json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))


def year_in(lo, hi, y):
    return isinstance(y, int) and isinstance(lo, int) and isinstance(hi, int) and lo <= y <= hi


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    world = load_world()
    pm = {p["id"]: (p.get("startYear"), p.get("endYear")) for p in world["periods"]}
    have_ev = {e["id"] for e in world["events"]}
    have_fig = {f["id"] for f in world["figures"]}

    # 先收集本批所有新 id，便于内部引用校验
    new_ids = set()
    records = []
    for path in sys.argv[1:]:
        data = json.load(io.open(path, encoding="utf-8"))
        recs = data if isinstance(data, list) else (
            data.get("events") or data.get("figures") or [])
        for rec in recs:
            if isinstance(rec, dict) and rec.get("id"):
                new_ids.add(rec["id"])
                records.append((os.path.basename(path), rec))

    conflicts, range_bad, ref_missing = [], [], []

    for fname, rec in records:
        rid = rec["id"]
        # 1) id 冲突
        if rid in have_ev or rid in have_fig:
            conflicts.append((fname, rid))

        pid = rec.get("periodId") or rec.get("p")
        lo, hi = pm.get(pid, (None, None))
        if lo is None:
            range_bad.append((rid, f"时期不存在: {pid}"))
            continue

        # 2) 事件区间
        y = rec.get("year", rec.get("y"))
        ye = rec.get("yearEnd", rec.get("ye"))
        if y is not None:
            ye = ye if ye is not None else y
            if not (year_in(lo, hi, y) and year_in(lo, hi, ye)):
                range_bad.append((rid, f"year={y}~{ye} 超出 [{lo},{hi}]"))

        # 3) 人物生卒年
        by = rec.get("birthYear")
        dy = rec.get("deathYear")
        if by is not None and not year_in(lo, hi, by):
            range_bad.append((rid, f"birthYear={by} 超出 [{lo},{hi}]"))
        span = (hi - lo) if isinstance(lo, int) and isinstance(hi, int) else 0
        if dy is not None and not year_in(lo, hi, dy):
            # 允许超出至多一个区间长度（人物生卒跨时期是常态）
            if not (isinstance(dy, int) and isinstance(hi, int) and dy <= hi + span):
                range_bad.append((rid, f"deathYear={dy} 远超 [{lo},{hi}]"))

        # 4) 引用
        for key in ("figures", "f"):
            for fid in rec.get(key) or []:
                if fid not in have_fig and fid not in new_ids:
                    ref_missing.append((rid, key, fid))
        for key in ("relatedEvents", "re"):
            for eid in rec.get(key) or []:
                if eid not in have_ev and eid not in new_ids:
                    ref_missing.append((rid, key, eid))
        for key in ("relatedFigures", "rf"):
            for fid in rec.get(key) or []:
                if fid not in have_fig and fid not in new_ids:
                    ref_missing.append((rid, key, fid))

    print(f"检查 {len(records)} 条记录（来自 {len(sys.argv) - 1} 个分片）")
    print()
    print(f"① id 冲突: {len(conflicts)}", conflicts if conflicts else "✓")
    print(f"② 区间越界: {len(range_bad)}")
    for x in range_bad:
        print("     ", x[0], "|", x[1])
    if not range_bad:
        print("      ✓")
    print(f"③ 缺失引用: {len(ref_missing)}")
    for x in ref_missing:
        print("     ", x[0], "|", x[1], "->", x[2])
    if not ref_missing:
        print("      ✓")

    ok = not (conflicts or range_bad or ref_missing)
    print()
    print("结论:", "全部合规 ✓" if ok else "存在问题，需修正")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
