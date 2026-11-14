# -*- coding: utf-8 -*-
"""v2.5.0 批次3：修复宋辽金时期的人物归属错误。

审计发现：

1) 宋太祖赵匡胤（927-976）、宋太宗赵炅（939-997）被归到 `cn-liao`（辽朝）
   —— 他们是北宋开国皇帝，绝不能挂在辽朝下。
2) 史弥远（1180-1233）是南宋权相，被列为「北宋」代表人物
   —— 北宋终于 1127 年，史弥远出生时北宋已亡 53 年。

修复：
  - 赵匡胤、赵炅 → cn-song-north（北宋）
  - 史弥远 → 已在 cn-song-south（南宋），需从北宋 keyFigures 移除
  - 索额图（1636-1703，康熙朝）被归到 cn-ming（明朝）→ cn-qing-early
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

FIXES = {
    "fig-zhao-kuangyin": "cn-song-north",   # 宋太祖，北宋开国
    "fig-zhao-guangyi": "cn-song-north",    # 宋太宗
    "fig-suo-shi": "cn-qing-early",         # 索额图，康熙朝（原误挂明朝）
}

# 需要从 keyFigures 中移除的 (时期 id, 人物 id)
KF_REMOVE = {
    "cn-song-north": ["fig-shi-jingzhang"],   # 史弥远是南宋人
    "cn-liao": ["fig-zhao-kuangyin", "fig-zhao-guangyi"],
}


def main():
    dry = "--dry-run" in sys.argv

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    by_id = {f["id"]: f for f in china["figures"]}
    pm = {p["id"]: p for p in china["periods"]}

    print("=== 修正人物 periodId ===")
    resolved = {}
    for fid, target in FIXES.items():
        f = by_id.get(fid)
        if not f:
            print(f"  ! {fid} 不存在")
            continue
        cur = f.get("periodId")
        if cur == target:
            continue
        if target not in pm:
            print(f"  ! 目标时期不存在: {target}")
            continue
        print(f"  {f['name']:10s} {f.get('birthYear')}~{f.get('deathYear')}  {cur:18s} → {target}")
        resolved[fid] = target

    # 补丁分片
    patterns = ["figdata_*.json", "china_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    pid_patched = 0
    kf_patched = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (
            (obj.get("figures") or []) + (obj.get("periods") or []))
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            rid = rec.get("id")
            # 1) 人物 periodId
            if rid in resolved:
                key = "p" if ("p" in rec and "periodId" not in rec) else "periodId"
                if rec.get(key) != resolved[rid]:
                    rec[key] = resolved[rid]
                    pid_patched += 1
                    changed = True
            # 2) 时期 keyFigures 移除
            if rid in KF_REMOVE:
                for key in ("keyFigures", "kf"):
                    if key in rec and isinstance(rec[key], list):
                        kept = [x for x in rec[key] if x not in KF_REMOVE[rid]]
                        if len(kept) != len(rec[key]):
                            rec[key] = kept
                            kf_patched += len(rec[key]) - len(kept)
                            changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"\npersonId 补丁 {pid_patched} 处；keyFigures 移除 {kf_patched} 项。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
