# -*- coding: utf-8 -*-
"""v2.1.0：修正 w-age-of-sail 时期区间，并核查相关时期。

背景：批次10 补入地理大发现事件后发现时期区间不符——
  w-age-of-sail 当前是 (1600,1700)，但大航海时代的主流事件（迪亚士1488、
  哥伦布1492、麦哲伦1519-1522）发生在 15 世纪末至 16 世纪初，
  落在 1600 年之后属于明显错位。

调整：
  w-age-of-sail  (1600,1700) → (1400,1650)
  理由：覆盖 1405 郑和下西洋、1487 迪亚士、1492 哥伦布、1519-1522 麦哲伦，
        至 1650 荷兰东印度公司成立（1602）与西班牙海上霸权衰落（17世纪中叶）。

注意：区间放宽后，原属 w-age-of-sail 的 1600 年事件（荷兰黄金时代、
葡萄牙印度洋霸权）仍在区间内，不受影响。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
NEW_SPAN = {
    "w-age-of-sail": (1400, 1650),
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
        p["startDateText"] = f"公元{lo}年"
        p["endDateText"] = f"公元{hi}年"
        changed += 1

    if changed and not dry:
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=1)
        print(f"\n已更新 {changed} 个时期。")
    elif changed:
        print("\n[dry-run] 未写入。")


if __name__ == "__main__":
    main()
