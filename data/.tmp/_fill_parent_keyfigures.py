# -*- coding: utf-8 -*-
"""v2.2.0 批次1：父级容器时期的 keyFigures 从子时期汇总。

问题：10 个时期 keyFigures 为空，其中两个是真正的「容器时期」——
  w-america-precol（前哥伦布美洲）下有 maya(3人) + mesoamerica(6人) + andes(4人) = 13 人
  w-east-asia（东亚诸国）下有 korea(4人) + japan(8人) = 12 人
这些父时期本身不直接拥有事件与人物，但用户点进「前哥伦布美洲」时
应看到其下属文明的代表人物汇总，而不是空白。

其余为空的是叶子时期（史前、雅利安时代、周朝、中世纪中国等），
它们没有归属人物，属正常——史前本无具名人物，周朝/中世纪中国的人物
归在中国史 scope，世界史视角下只作容器。

做法：对「有子时期」的父时期，递归汇总子时期 keyFigures（去重、保序）。
改为源分片 world_periods.json。
"""
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
    pm = {p["id"]: p for p in world["periods"]}

    # 建父子索引
    children = {}
    for p in world["periods"]:
        pid = p.get("parentId")
        if pid:
            children.setdefault(pid, []).append(p["id"])

    def collect(pid, depth=0):
        """递归收集某时期及其子时期的 keyFigures（保序去重）。"""
        if depth > 5:
            return []
        out = []
        p = pm.get(pid)
        if p:
            out.extend(p.get("keyFigures") or [])
        for child in children.get(pid, []):
            out.extend(collect(child, depth + 1))
        return list(dict.fromkeys(out))

    # 目标：有子时期但 keyFigures 为空的父时期
    targets = {}
    for p in world["periods"]:
        pid = p["id"]
        if not children.get(pid):
            continue
        if p.get("keyFigures"):
            continue
        gathered = collect(pid)[:8]
        if gathered:
            targets[pid] = gathered

    if not targets:
        print("无需改动。")
        return

    print("将汇总以下父时期的 keyFigures：")
    for pid, fids in targets.items():
        names = [fig_by_id[f].get("name", f) for f in fids]
        print(f"  {pid}: {names}")

    # 补丁源分片
    path = os.path.join(HERE, "world_periods.json")
    shard = json.load(io.open(path, encoding="utf-8"))
    periods = shard if isinstance(shard, list) else shard.get("periods", [])

    patched = 0
    for p in periods:
        pid = p.get("id")
        if pid not in targets:
            continue
        key = "kf" if "kf" in p else "keyFigures"
        p[key] = targets[pid]
        patched += 1

    if patched and not dry:
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=1)
        print(f"\n已补 {patched} 个父时期。")
    elif dry:
        print("\n[dry-run] 未写入。")


if __name__ == "__main__":
    main()
