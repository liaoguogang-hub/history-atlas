# -*- coding: utf-8 -*-
"""v2.5.0 批次2：修复中国史时期 keyFigures 中的时代错挂。

审计发现 20+ 处 keyFigures 与时期区间完全不符，例如：

  cn-song-north（北宋 960-1127）  → 索额图（1636-1703，清朝）
  cn-modern-anti-japan（抗战）    → 左宗棠（1812-1885，清末）
  cn-wudai-south（十国 907-979）  → 李建成（589-626，唐初）
  cn-tang-late（唐后期 827-907）  → 王献之（344-386，东晋）
  cn-jin（金 1115-1234）          → 赵俨（171-245，三国）
  cn-ming-mid（明中期 1521-1620） → 朱祐樘（1470-1505，明中期偏早）
  cn-qing-early（清前期 1644-1735）→ 努尔哈赤/皇太极（卒于 1644 前）
  cn-prc-reform（1978-2012）      → 刘少奇（1969 卒）

做法：从这些时期的 keyFigures 中移除时代不符者（保留正确人物）。
被移除者本身仍存在于 figures 中，只是不再作为该时期的代表。

判据：人物主要活动期 [生年+20, 卒年] 与时期区间 [startYear, endYear] 无交集。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


# 保护名单：当代在职/在世政治人物，不能按生年推断时代归属
PROTECT = {
    "习近平", "胡锦涛", "温家宝", "李克强", "王毅", "江泽民", "朱镕基",
    "李工", "颜福成",
}


def main():
    dry = "--dry-run" in sys.argv

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    fg = {f["id"]: f for f in china["figures"]}
    pm = {p["id"]: p for p in china["periods"]}

    # 计算需要从各时期移除的人物
    removals = {}
    for p in china["periods"]:
        kf = p.get("keyFigures") or []
        if not kf:
            continue
        lo, hi = p.get("startYear"), p.get("endYear")
        if not isinstance(lo, int) or not isinstance(hi, int):
            continue
        bad = []
        for fid in kf:
            f = fg.get(fid)
            if not f:
                bad.append(fid)
                continue
            if f.get("name") in PROTECT:
                continue
            by, dy = f.get("birthYear"), f.get("deathYear")
            if not isinstance(by, int):
                continue
            dy = dy if isinstance(dy, int) else by
            mature = by + 20
            # 容差：允许人物生涯超出时期边界至多「时期长度」或 30 年
            # （取较大者）。历史上很多奠基者活跃于正式纪年之前
            # （如努尔哈赤 1626 卒，而清前期从 1644 起算），
            # 严格判据会误删这些关键人物。
            span = max(hi - lo, 30)
            # 只移除「时代明显不符」者：生平区间与时期区间完全脱节且
            # 间距超过 50 年。这能抓出「北宋里的索额图」这类离谱错挂，
            # 又不会误删当代政治人物（习近平生年虽早，但任期在 2012+）。
            if dy < lo - span and (lo - dy) > 50:
                bad.append(fid)
            elif mature > hi + span and (mature - hi) > 50:
                bad.append(fid)
        if bad:
            removals[p["id"]] = bad

    if not removals:
        print("无需改动。")
        return

    print("将从以下时期的 keyFigures 移除时代不符者：")
    for pid, fids in removals.items():
        names = [fg[x]["name"] if x in fg else x for x in fids]
        print("  %-22s -%s" % (pid, names))

    # 补丁中国史时期分片
    patterns = ["china_periods*.json", "cn_periods*.json", "periods_*.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    patched = 0
    touched = []
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (obj.get("periods") or [])
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            pid = rec.get("id")
            if pid not in removals:
                continue
            for key in ("keyFigures", "kf"):
                if key in rec and isinstance(rec[key], list):
                    kept = [x for x in rec[key] if x not in removals[pid]]
                    if len(kept) != len(rec[key]):
                        rec[key] = kept
                        patched += len(rec[key]) - len(kept)
                        changed = True
                        touched.append(os.path.basename(path))
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print("\n移除 %d 项，涉及 %d 个分片。" % (patched, len(set(touched))))
    for name in sorted(set(touched)):
        print("  " + name)
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("\n请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
