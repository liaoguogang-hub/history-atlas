# -*- coding: utf-8 -*-
"""v2.1.0：拓宽 w-cold-war 时期区间。

背景：批次11 要给冷战时期补人物，但发现原区间 (1945,1990) 太窄——
冷战的核心人物生于 1913—1931（杜鲁门 1884、丘吉尔 1874、斯大林 1878、
赫鲁晓夫 1894、马歇尔 1880、尼克松 1913、肯尼迪 1917、卡斯特罗 1926、
戈尔巴乔夫 1931）。若时期只从 1945 起，这些人物在归期算法
（reassign_figures.py：按生卒年在同组内选最窄时期）中永远无法归入，
w-cold-war 将始终是 0 人物。

调整：w-cold-war (1945,1990) → (1914,1990)
  起点与 w-contemporary（1914）一致，也与 w-world-wars（1914-1945）相接，
  符合「两次世界大战 → 冷战」的历史连续性。

预期效果：
  - 生于 1914-1990 区间内的冷战人物（肯尼迪、尼克松、卡斯特罗、戈尔巴乔夫等）
    会被自动归入 w-cold-war
  - 生于 1874-1894 的（丘吉尔、斯大林、杜鲁门、马歇尔、赫鲁晓夫）留在 w-modern，
    这是合理的——他们在近代时期已活跃，冷战只是其生涯的后段

注意：区间变化会影响事件归属校验，改后必须重跑 build_data.py。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
NEW_SPAN = {"w-cold-war": (1914, 1990)}


def main():
    dry = "--dry-run" in sys.argv
    path = os.path.join(HERE, "world_periods.json")
    shard = json.load(io.open(path, encoding="utf-8"))
    periods = shard if isinstance(shard, list) else shard.get("periods", [])

    changed = 0
    for p in periods:
        pid = p.get("id")
        if pid not in NEW_SPAN:
            continue
        lo, hi = NEW_SPAN[pid]
        old = (p.get("startYear"), p.get("endYear"))
        if old == (lo, hi):
            print(f"  · {pid}: 已是目标区间")
            continue
        print(f"  ✓ {pid}: {old} → ({lo}, {hi})")
        p["startYear"] = lo
        p["endYear"] = hi
        p["startDateText"] = f"公元{lo}年"
        p["endDateText"] = f"公元{hi}年"
        changed += 1

    if changed and not dry:
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=1)
        print(f"\n已更新 {changed} 个时期。")
        print("请运行 python tools/build_data.py 复核。")
    elif changed:
        print("\n[dry-run] 未写入。")


if __name__ == "__main__":
    main()
