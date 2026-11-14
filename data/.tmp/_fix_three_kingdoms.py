# -*- coding: utf-8 -*-
"""v2.5.0 批次1：三国与南北朝人物归位。

问题一：三国核心人物全被归到「东汉」
  cn-han-east（东汉，25-220）下有 54 人，其中包含曹操、刘备、孙权、
  诸葛亮、关羽、周瑜、司马懿、赵云、张飞——他们生于东汉末年，
  但历史地位属于三国时期（220-280）。
  结果：「三国」时期 0 人物，而「东汉」堆积 54 人。

问题二：南北朝父时期 0 人物
  南北朝的人物分散在 11 个子时期（cn-nanbei-north / cn-nanbei-south 等），
  父时期 cn-nanbei 本身没有 keyFigures，用户点进「南北朝」看不到人物。

修复：
  1) 三国人物按「主要活动时期」归入 cn-three-wei / cn-three-shu / cn-three-wu
  2) 给 cn-nanbei 汇总子时期代表人物

★ 注意：改分片不够，必须同时写 PERIOD_OVERRIDE，否则 reassign_figures.py
  按生卒年会把它们拉回 cn-han-east（他们多生于 155-185 年，落在东汉区间）。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 人物 id : 目标 periodId
FIXES = {
    # 曹魏
    "fig-han-east-cao-cao": "cn-three-wei",
    "fig-han-east-cao-pi": "cn-three-wei",
    "fig-han-east-cao-rui": "cn-three-wei",
    "fig-sima-yi": "cn-three-wei",
    "fig-sima-zhao": "cn-three-wei",
    "fig-deng-ai": "cn-three-wei",
    "fig-zhong-hui": "cn-three-wei",
    "fig-guo-jia": "cn-three-wei",
    "fig-xun-yu": "cn-three-wei",
    # 蜀汉
    "fig-liu-bei": "cn-three-shu",
    "fig-zhuge-liang": "cn-three-shu",
    "fig-guan-yu": "cn-three-shu",
    "fig-zhang-fei": "cn-three-shu",
    "fig-zhao-yun": "cn-three-shu",
    "fig-jiang-wei": "cn-three-shu",
    # 孙吴
    "fig-sunquan": "cn-three-wu",
    "fig-zhou-yu": "cn-three-wu",
    "fig-lu-su": "cn-three-wu",
    "fig-lu-xun": "cn-three-wu",
    "fig-lv-meng": "cn-three-wu",
    "fig-taishi-ci": "cn-three-wu",
}


def main():
    dry = "--dry-run" in sys.argv

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    by_id = {f["id"]: f for f in china["figures"]}
    pm = {p["id"]: p for p in china["periods"]}

    resolved = {}
    for fid, target in FIXES.items():
        f = by_id.get(fid)
        if not f:
            continue
        cur = f.get("periodId")
        if cur == target:
            continue
        if target not in pm:
            print(f"  ! 目标时期不存在: {target}")
            continue
        resolved[fid] = target
        print(f"  {f['name']:10s} {f.get('birthYear')}~{f.get('deathYear')}  {cur:20s} → {target}")

    if not resolved:
        print("无需改动。")
        return

    # 补丁中国史分片
    patterns = ["figdata_*.json", "china_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
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
        recs = obj if isinstance(obj, list) else (obj.get("figures") or [])
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            fid = rec.get("id")
            if fid in resolved:
                key = "p" if ("p" in rec and "periodId" not in rec) else "periodId"
                if rec.get(key) != resolved[fid]:
                    rec[key] = resolved[fid]
                    patched += 1
                    changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"\n补丁 {patched} 处。")
    print("\n必须同时更新 tools/reassign_figures.py 的 PERIOD_OVERRIDE，")
    print("否则按生卒年归位会把他们拉回 cn-han-east。")
    if dry:
        print("[dry-run] 未写入。")


if __name__ == "__main__":
    main()
