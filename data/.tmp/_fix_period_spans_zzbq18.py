# -*- coding: utf-8 -*-
"""v2.1.0：调整三个古代时期的区间以匹配史实。

背景：批次9 补入亚述与迈锡尼的人物后，发现时期区间与史实不符：
  w-assyrian   [-2025,-801]  —— 但亚述帝国实际延续到公元前609年（尼尼微陷落）
  w-mycenaean  [-1750,-1100] —— 迈锡尼人物（阿伽门农等）约前1500年，尚可，
                                  但迈锡尼文明崩溃在约前1200年，区间偏宽
  w-minoan     [-3000,-1450] —— 米诺斯人物（米诺斯）约前2900年，在区间内 ✓

调整：
  w-assyrian   → [-2025,-601]  （覆盖亚述帝国全期至萨贡王被弑/帝国终局）
  w-mycenaean  → [-1600,-1100] （迈锡尼文明的实际存续期）

注意：区间变化会影响「事件是否落在时期内」的校验。
本脚本只改 periods 的 startYear/endYear，不动事件归属；
改后必须重跑 build_data.py 确认 ERROR=0。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

NEW_SPAN = {
    # 时期 id : (新起始年, 新结束年)
    "w-assyrian": (-2025, -601),
    "w-mycenaean": (-1600, -1100),
}


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
        # 同步日期文本
        if lo < 0:
            p["startDateText"] = f"公元前{abs(lo)}年"
        else:
            p["startDateText"] = f"公元{lo}年"
        if hi < 0:
            p["endDateText"] = f"公元前{abs(hi)}年"
        else:
            p["endDateText"] = f"公元{hi}年"
        changed += 1

    if changed and not dry:
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=1)
        print(f"\n已更新 {changed} 个时期（源分片 world_periods.json）。")
        print("请运行 python tools/build_data.py 复核。")
    elif changed:
        print("\n[dry-run] 未写入。")


if __name__ == "__main__":
    main()
