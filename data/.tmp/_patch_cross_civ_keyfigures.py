# -*- coding: utf-8 -*-
"""v2.0.0 批次2：为 w-cross-civilization 各时期补 keyFigures（改源分片）。

问题：跨文明交流下 6 个子时期共 100 个事件（占世界史 23%），
但每个子时期的 keyFigures 全为 0 —— 该时期在「人物志」维度完全空白。

实测：这 100 个事件**已经引用了 126 个人物**，只是没有回填到 period.keyFigures。
因此把各时期事件中高频出现的人物填进去即可，不新建任何条目。

★ 关键：必须改 data/.tmp/world_periods.json（源分片），
  直接改 data/world.json 会被 build_data.py 覆盖。
  world_periods.json 用缩写键 kf（= keyFigures）。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PERIODS = os.path.join(HERE, "world_periods.json")
WORLD = os.path.join(ROOT, "data", "world.json")

LIMIT = {
    "w-cross-civilization": 8,
    "w-cc-prehistoric": 3,
    "w-cc-classical": 6,
    "w-cc-medieval": 8,
    "w-cc-oceanic": 6,
    "w-cc-industrial": 6,
    "w-cc-contemporary": 6,
}


def main():
    # 用最终产物统计频次（数据最全）
    world = json.load(io.open(WORLD, encoding="utf-8"))
    figure_by_id = {f["id"]: f for f in world["figures"]}

    freq = {pid: {} for pid in LIMIT}
    for e in world["events"]:
        pid = e.get("periodId")
        if pid not in LIMIT:
            continue
        for fid in e.get("figures") or []:
            if fid in figure_by_id:
                freq[pid][fid] = freq[pid].get(fid, 0) + 1

    # 顶层容器：汇总所有子时期
    agg = {}
    for child, counts in freq.items():
        if child == "w-cross-civilization":
            continue
        for fid, n in counts.items():
            agg[fid] = agg.get(fid, 0) + n
    freq["w-cross-civilization"] = agg

    wanted = {}
    for pid, limit in LIMIT.items():
        counts = freq.get(pid) or {}
        if not counts:
            print(f"  · {pid}: 无关联人物，跳过")
            continue
        ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        wanted[pid] = [fid for fid, _ in ranked[:limit]]

    # 补丁源分片
    shard = json.load(io.open(PERIODS, encoding="utf-8"))
    periods = shard if isinstance(shard, list) else shard.get("periods", [])

    patched = 0
    for p in periods:
        pid = p.get("id")
        if pid not in wanted:
            continue
        # 兼容缩写键 kf 与全称 keyFigures
        key = "kf" if "kf" in p or "keyFigures" not in p else "keyFigures"
        old = p.get(key) or []
        new = wanted[pid]
        if old == new:
            print(f"  · {pid}: 已是最新")
            continue
        p[key] = new
        patched += 1
        names = [figure_by_id[f].get("name", f) for f in new]
        print(f"  ✓ {pid}: {len(new)} 人 → {names}")

    if patched:
        with io.open(PERIODS, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=1)
        print(f"\n已补丁 {patched} 个时期（源分片 {os.path.basename(PERIODS)}）。")
    else:
        print("\n无需改动。")


if __name__ == "__main__":
    main()
