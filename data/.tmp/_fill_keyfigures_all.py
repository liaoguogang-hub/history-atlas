# -*- coding: utf-8 -*-
"""v2.1.0 批次12：为所有时期的 keyFigures 回填代表人物。

问题（全局性）：
  76 个时期有事件、也有人物归属，但 period.keyFigures 全部为空。
  App 的时期详情页按 keyFigures 展示代表人物，这些时期会显示空白，
  用户点进「罗马帝国」「文艺复兴」「冷战」等核心时期看不到任何人物。

做法：
  对每个时期，取其下事件所引用的 figures 出现频次，以及
  归属该时期（periodId）的人物，合并排序后取前 N 位写入 keyFigures。
  N 按该时期人物数自适应：3-8 位。

改为源分片：
  - world_periods.json（主要）
  - world_periods_zzbq10.json / world_periods_zzbq13.json（新时期的定义分片）

注意：`w-cc-*` 已在 v2.0.0 由 group_cross_civ.py 处理，本脚本跳过。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 每个时期的 keyFigures 上限（按人物规模自适应）
def limit_for(n_owned, n_ref):
    total = n_owned + n_ref
    if total <= 2:
        return total
    if total <= 4:
        return 3
    if total <= 8:
        return total
    return 8


def main():
    dry = "--dry-run" in sys.argv

    world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))
    fig_by_id = {f["id"]: f for f in world["figures"]}

    # 1) 统计：每个时期 → 归属人物 + 事件引用人物频次
    owned = {}
    for f in world["figures"]:
        pid = f.get("periodId")
        if pid:
            owned.setdefault(pid, []).append(f["id"])

    ref = {}
    for e in world["events"]:
        pid = e.get("periodId")
        if not pid:
            continue
        for fid in e.get("figures") or []:
            if fid in fig_by_id:
                ref.setdefault(pid, {})
                ref[pid][fid] = ref[pid].get(fid, 0) + 1

    # 2) 生成期望的 keyFigures
    wanted = {}
    for p in world["periods"]:
        pid = p["id"]
        if pid.startswith("w-cc-"):
            continue                      # 已由 group_cross_civ.py 处理
        own = owned.get(pid, [])
        refs = ref.get(pid, {})
        if not own and not refs:
            continue

        # 排序信号（无 importance 字段，改用可观测的代表性指标）：
        #   1) 事件引用频次（被多少事件提及）——最能反映其历史分量
        #   2) biography 长度（资料充实度，间接反映编纂时的重视程度）
        #   3) 生年（稳定的最终 tie-break）
        def score(fid):
            f = fig_by_id[fid]
            n_ref = refs.get(fid, 0)
            bio_len = len((f.get("biography") or ""))
            by = f.get("birthYear") or 0
            dy = f.get("deathYear")
            dy = dy if isinstance(dy, int) else by

            # 时期契合度：人物「成熟期」（生年后 25 年起）与时期区间的重叠比例。
            # 这能识别「生于此时、成名于后世」的人物——如屠呦呦生于 1930
            # 但成熟期在 1955 年后，对 w-world-wars(1914-1945) 的契合度为 0。
            fit = 0.0
            if isinstance(s_year, int) and isinstance(e_year, int):
                mature = by + 25
                lo, hi = max(mature, s_year), min(max(dy, mature), e_year)
                if hi >= lo:
                    span = max(1, e_year - s_year)
                    fit = (hi - lo) / span
            return (-round(fit, 2), -n_ref, -bio_len, by)

        # 过滤跨期污染：只保留「归属本时期」或「生卒年与时期区间重叠」的人物。
        # 否则事件里引用的跨时代人物（如文艺复兴事件提及伊本·赫勒敦）
        # 会被误列为该时期代表人物。
        s_year, e_year = p.get("startYear"), p.get("endYear")

        def overlaps(fid):
            if fid in own:
                return True
            f = fig_by_id[fid]
            by, dy = f.get("birthYear"), f.get("deathYear")
            if not isinstance(by, int) or not isinstance(s_year, int):
                return False
            dy = dy if isinstance(dy, int) else by
            hi_bound = e_year if isinstance(e_year, int) else 99999
            # 要求「主要活跃期」与时期区间有实质交集：
            #   以生卒年区间与时期区间取交集，且交集长度 >= 时期长度的 1/4，
            #   避免「生于时期之后」或「仅擦边」的人物混入。
            lo = max(by, s_year)
            hi = min(dy, hi_bound)
            if hi < lo:
                return False
            span = max(1, hi_bound - s_year)
            return (hi - lo) >= span * 0.25

        # 窄时期（跨度 <= 60 年）的人物归属最精确，只用归属人物；
        # 事件引用容易带入「生于此时、成名于后世」的人物（如屠呦呦生于 1930
        # 但成就于 1970 年代，不应作为两次世界大战的代表）。
        span_narrow = isinstance(s_year, int) and isinstance(e_year, int) and (e_year - s_year) <= 60
        pool = set(own) if (span_narrow and own) else {i for i in (set(own) | set(refs)) if overlaps(i)}
        merged = sorted(pool, key=score)
        wanted[pid] = merged[:limit_for(len(own), len(refs))]

    # 3) 补丁各时期分片
    shard_files = [
        "world_periods.json",
        "world_periods_zzbq10.json",
        "world_periods_zzbq13.json",
    ]
    total_patched = 0
    for name in shard_files:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        shard = json.load(io.open(path, encoding="utf-8"))
        periods = shard if isinstance(shard, list) else shard.get("periods", [])
        changed = 0
        for p in periods:
            pid = p.get("id")
            if pid not in wanted:
                continue
            new = wanted[pid]
            # 兼容缩写键 kf
            key = "kf" if "kf" in p else "keyFigures"
            old = p.get(key) or []
            if old == new:
                continue
            p[key] = new
            changed += 1
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(shard, f, ensure_ascii=False, indent=1)
            print(f"  ✓ {name}: 补 {changed} 个时期")
            total_patched += changed
        elif changed:
            print(f"  · {name}: 待补 {changed} 个时期（dry-run）")

    print()
    print(f"共补 {total_patched} 个时期的 keyFigures。")

    # 4) 自检
    if not dry:
        remain = [p["id"] for p in world["periods"]
                  if not p["id"].startswith("w-cc-")
                  and not (p.get("keyFigures") or [])
                  and (owned.get(p["id"]) or ref.get(p["id"]))]
        print(f"仍为空的时期（重建前统计）：{len(remain)} 个")
        if remain[:8]:
            print("  示例:", remain[:8])
    print("\n请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
