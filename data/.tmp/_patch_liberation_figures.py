# -*- coding: utf-8 -*-
"""v2.7.0 批次2：为解放战争剩余 2 个空 figures 的事件补人物关联。

「解放战争」（1946，全面内战爆发）与「辽沈战役」（1948）的 figures 为空，
导致事件详情页看不到任何相关人物。

补：
  ev-解放战争  → 毛泽东、蒋介石、周恩来（决策层）
  ev-辽沈战役  → 林彪、罗荣桓、卫立煌？（卫不在库，只补在库者）
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

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    fig_ids = {f["id"] for f in china["figures"]}

    # 事件 id : 人物 id 列表
    PATCH = {}
    for e in china["events"]:
        if e.get("periodId") != "cn-modern-liberation":
            continue
        if e.get("figures"):
            continue
        name = e.get("name") or ""
        if "解放战争" in name and "胜利" not in name:
            PATCH[e["id"]] = ["fig-mao-zedong", "fig-zzbq27-chiang", "fig-zhou-enlai"]
        elif "辽沈" in name:
            PATCH[e["id"]] = ["fig-lin-biao", "fig-zzbq27-luo"]
        elif "平津" in name:
            PATCH[e["id"]] = ["fig-zzbq27-fuzuoyi", "fig-zzbq27-linbiao"]
        elif "锦州" in name:
            PATCH[e["id"]] = ["fig-lin-biao", "fig-zzbq27-luo"]

    # 过滤不存在的 id
    for eid, fids in list(PATCH.items()):
        valid = [f for f in fids if f in fig_ids]
        missing = [f for f in fids if f not in fig_ids]
        if missing:
            print("  ! %s 跳过不存在: %s" % (eid, missing))
        if valid:
            PATCH[eid] = valid
        else:
            del PATCH[eid]

    if not PATCH:
        print("无可补全项。")
        return

    print("将补全：")
    fg = {f["id"]: f["name"] for f in china["figures"]}
    for eid, fids in PATCH.items():
        print("  %-28s ← %s" % (eid, [fg[f] for f in fids]))

    # 补丁分片
    patterns = ["china_events_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    patched = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (obj.get("events") or [])
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            eid = rec.get("id")
            if eid not in PATCH:
                continue
            key = "f" if ("f" in rec and "figures" not in rec) else "figures"
            cur = rec.get(key) or []
            merged = list(dict.fromkeys(cur + PATCH[eid]))
            if merged != cur:
                rec[key] = merged
                patched += 1
                changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print("\n补丁 %d 个事件。" % patched)
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
