# -*- coding: utf-8 -*-
"""v2.4.0 批次2：清理地区时期 keyFigures 中的残留错挂项。

问题：上一步修正了人物的 periodId，但 `keyFigures` 是源分片里写死的缓存，
不会自动跟着变。审计发现两个残留：

  w-old-world（古代非洲）      keyFigures = ['fig-jiang-ziya']   ← 姜子牙，归属人物已为 0
  w-modern-south-asia（近代南亚）keyFigures 含 'fig-victoria'      ← 英国女王

修复：
  - 对「归属人物为 0」的时期，清空 keyFigures
  - 对「归属人物 > 0」的时期，只保留归属本时期的人物

注意：`w-near-east-persian` 的希罗多德已正确移除（因为它的归属已改为希腊），
      这里仅做兜底一致性检查。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    dry = "--dry-run" in sys.argv

    world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))
    fig_by_id = {f["id"]: f for f in world["figures"]}

    # 统计每个时期的归属人物
    owned = {}
    for f in world["figures"]:
        pid = f.get("periodId")
        if pid:
            owned.setdefault(pid, set()).add(f["id"])

    # 有子时期的父容器不受此约束（它们汇总子时期）
    children = {}
    for p in world["periods"]:
        pid = p.get("parentId")
        if pid:
            children.setdefault(pid, []).append(p["id"])

    # 只处理「地区专题时期」——这类时期的人物必须严格属于该地区。
    # 编年时期（如 w-world-wars、w-cold-war）的代表人物可以包括
    # 归属在其他时期但同时代的关键人物（斯大林归 w-imperialism，
    # 但他是 w-world-wars 的代表人物，这是合理的）。
    REGION_ONLY = {
        "w-ancient-south-asia", "w-medieval-south-asia", "w-modern-south-asia",
        "w-mughal", "w-medieval-southeast-asia", "w-southeast-asia",
        "w-modern-southeast-asia", "w-old-world", "w-africa-west",
        "w-africa-east", "w-modern-africa", "w-america-precol", "w-maya",
        "w-mesoamerica", "w-andes", "w-latin-america", "w-east-asia",
        "w-korea", "w-japan", "w-oceania", "w-near-east-persian",
    }

    fixes = {}
    for p in world["periods"]:
        pid = p["id"]
        if pid not in REGION_ONLY:
            continue
        if children.get(pid):
            continue                      # 父容器跳过（汇总子时期）
        kf = p.get("keyFigures") or []
        if not kf:
            continue
        own = owned.get(pid, set())
        if not own:
            fixes[pid] = []
        else:
            kept = [x for x in kf if x in own]
            if kept != kf:
                fixes[pid] = kept

    if not fixes:
        print("无需改动。")
        return

    print("将修正以下时期的 keyFigures：")
    for pid, kf in fixes.items():
        names = [fig_by_id[x].get("name", x) if x in fig_by_id else x for x in kf]
        print(f"  {pid:26s} → {names if names else '[]（清空）'}")

    # 补丁源分片
    patched = 0
    for path in sorted(glob.glob(os.path.join(HERE, "world_periods*.json"))):
        shard = json.load(io.open(path, encoding="utf-8"))
        periods = shard if isinstance(shard, list) else shard.get("periods", [])
        changed = False
        for p in periods:
            pid = p.get("id")
            if pid not in fixes:
                continue
            for key in ("keyFigures", "kf"):
                if key in p:
                    p[key] = fixes[pid]
                    changed = True
                    patched += 1
                    break
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(shard, f, ensure_ascii=False, indent=1)

    print(f"\n补丁 {patched} 处。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
