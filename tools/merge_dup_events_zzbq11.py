# -*- coding: utf-8 -*-
"""合并中国史中的重复事件（同一事件被重复收录）。

审计发现的重复对：
  保留(内容更优)              删除(重复)                依据
  ev-han-chimei 文景之治      ev-han-wenjing           前者 detail 540字，后者 242字
  ev-han-huangjin 黄巾起义    ev-han-yellow-turban     前者叙述更完整清晰
  ev-three-yiling 夷陵之战    ev-weijin-yiling         前者含完整战略分析

做三件事：
1. 把「待删条目」上的人物引用迁移到「保留条目」（figures 取并集）
2. 把人物/时期里指向「待删条目」的 relatedEvents 改指向「保留条目」
3. 从分片中删除「待删条目」

⚠ 只改源分片，保证 build_data 重建后不复活。

用法：
    python tools/merge_dup_events_zzbq11.py [--dry-run]
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "data", ".tmp")

# 保留 -> 删除列表
MERGES = {
    # 第一批（同年重复，内容更优者保留）
    "ev-han-chimei": ["ev-han-wenjing"],
    "ev-han-huangjin": ["ev-han-yellow-turban"],
    "ev-three-yiling": ["ev-weijin-yiling"],
    # 第二批（审计发现的同年重复对，按 detail 长度保留更优者）
    "ev-zzbq2-chenqiao": ["ev-wudai-song-founding"],      # 陈桥兵变 359字 > 北宋建立 201字
    "ev-weijin-taikang": ["ev-jin-taiping"],              # 太康之治 211字 > 177字
    "ev-zzbq4-nibuchu": ["ev-qing-yaksa"],                # 雅克萨+尼布楚 359字 > 196字
    "ev-wudai-houjin": ["ev-wudai-yanyun"],               # 后晋建立 209字 > 193字
    "ev-jin-yongjia": ["ev-weijin-yongjia"],              # 永嘉之乱 489字 > 216字
    "ev-three-gaopingling": ["ev-weijin-sima-power"],     # 高平陵之变 511字 > 256字
    "ev-tang-kaixuan": ["ev-tang-kaiyuan"],               # 开元盛世 449字 > 250字
}

CHINA_SHARDS = [
    os.path.join(TMP, "evdata_*.json"),
    os.path.join(TMP, "figdata_*.json"),
    os.path.join(TMP, "china_*.json"),   # china_periods.json / china_ev_fill*.json / china_fig_fill*.json
    os.path.join(TMP, "_b*.json"),       # _b2b.json / _b3.json 等历史填充分片
    os.path.join(TMP, "_mine.json"),
]


def load_shards():
    out = {}
    for pat in CHINA_SHARDS:
        for p in sorted(glob.glob(pat)):
            try:
                out[p] = json.load(io.open(p, encoding="utf-8"))
            except Exception as exc:                 # noqa: BLE001
                print(f"  ! 跳过 {os.path.basename(p)}: {exc}")
    return out


def iter_records(obj):
    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                yield it
    elif isinstance(obj, dict):
        for key in ("events", "figures", "periods"):
            for it in obj.get(key) or []:
                if isinstance(it, dict):
                    yield it


def find_records(shards, target_id):
    """返回 [(shard_path, container, index, record)]"""
    hits = []
    for path, obj in shards.items():
        if isinstance(obj, list):
            for i, it in enumerate(obj):
                if isinstance(it, dict) and it.get("id") == target_id:
                    hits.append((path, obj, i, it))
        elif isinstance(obj, dict):
            for key in ("events", "figures", "periods"):
                lst = obj.get(key)
                if isinstance(lst, list):
                    for i, it in enumerate(lst):
                        if isinstance(it, dict) and it.get("id") == target_id:
                            hits.append((path, lst, i, it))
    return hits


def rec_name(rec):
    """名称可能是 name 或缩写 n。"""
    return rec.get("name") or rec.get("n") or "?"


def rec_figures(rec):
    """人物引用列表可能是 figures 或缩写 f。"""
    for key in ("figures", "f"):
        v = rec.get(key)
        if isinstance(v, list):
            return v
    return None


def main():
    dry = "--dry-run" in sys.argv
    shards = load_shards()
    print(f"扫描 {len(shards)} 个中国史分片")

    # ---------- 预检 ----------
    plan = []
    for keep, drops in MERGES.items():
        kh = find_records(shards, keep)
        if not kh:
            # 保留条目由 backfill_missing.py / 词典生成（不在分片中），
            # 仍可安全删除重复条目，只是无法合并 figures。
            print(f"  · 保留条目 {keep} 由流水线词典生成，仅执行删除")
            for d in drops:
                dh = find_records(shards, d)
                if not dh:
                    print(f"  ! {d} 在源分片中不存在，跳过")
                    continue
                plan.append((keep, d, dh))
            continue
        for d in drops:
            dh = find_records(shards, d)
            if not dh:
                print(f"  ! {d} 在源分片中不存在（可能已在别处合并），跳过")
                continue
            plan.append((keep, d, dh))

    print("\n合并计划：")
    for keep, drop, hits in plan:
        for path, _c, _i, rec in hits:
            print(f"  {drop} ({rec_name(rec)}) [{os.path.basename(path)}] → 合并进 {keep}")

    if dry:
        print("\n[dry-run] 未写入。")
        return

    # ---------- 执行合并 ----------
    # 第一步：把引用改指向保留条目（不动结构）
    ref_fixed = 0
    for keep, drop, _hits in plan:
        for obj in shards.values():
            for it in iter_records(obj):
                for key in ("relatedEvents", "re"):
                    lst = it.get(key)
                    if isinstance(lst, list):
                        for i, v in enumerate(lst):
                            if v == drop:
                                lst[i] = keep
                                ref_fixed += 1
    print(f"  引用改指向：{ref_fixed} 处")

    # 第二步：合并 figures（取并集）
    for keep, drop, hits in plan:
        keep_rec = None
        for _path, _c, _i, rec in find_records(shards, keep):
            keep_rec = rec
            break
        if keep_rec is None:
            print(f"  ! 找不到保留条目 {keep}，跳过 figures 合并")
            continue
        kf = rec_figures(keep_rec)
        if not isinstance(kf, list):
            continue
        for _p, _c, _i, rec in hits:
            for fid in rec_figures(rec) or []:
                if fid not in kf:
                    kf.append(fid)

    # 第三步：统一删除被删条目的「定义」（按 id 精确匹配，从后往前删）
    for _keep, drop, _hits in plan:
        removed = 0
        for path, obj in shards.items():
            if isinstance(obj, list):
                for i in range(len(obj) - 1, -1, -1):
                    it = obj[i]
                    if isinstance(it, dict) and it.get("id") == drop:
                        del obj[i]
                        removed += 1
            elif isinstance(obj, dict):
                for key in ("events", "figures", "periods"):
                    lst = obj.get(key)
                    if not isinstance(lst, list):
                        continue
                    for i in range(len(lst) - 1, -1, -1):
                        it = lst[i]
                        if isinstance(it, dict) and it.get("id") == drop:
                            del lst[i]
                            removed += 1
        print(f"  已删除 {drop} 的定义 {removed} 处")

    # ---------- 写回 ----------
    written = 0
    for path, obj in shards.items():
        with io.open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
        written += 1
    print(f"\n写回 {written} 个分片。")

    # ---------- 自检：被删条目不得仍有「定义」残留 ----------
    # 注意：引用（relatedEvents 等）在合并阶段已被改指向保留条目，
    # 因此这里只检查是否有分片仍然「定义」了被删的 id。
    leftovers = []
    for pat in CHINA_SHARDS:
        for path in glob.glob(pat):
            try:
                obj = json.load(io.open(path, encoding="utf-8"))
            except Exception:                        # noqa: BLE001
                continue
            for it in iter_records(obj):
                if it.get("id") in [d for ds in MERGES.values() for d in ds]:
                    leftovers.append((os.path.basename(path), it.get("id")))
    if leftovers:
        raise SystemExit(f"自检失败：仍存在被删条目的定义 {leftovers}")

    # 再确认引用中也不残留
    for pat in CHINA_SHARDS:
        for path in glob.glob(pat):
            txt = io.open(path, encoding="utf-8").read()
            for drops in MERGES.values():
                for d in drops:
                    if f'"{d}"' in txt:
                        print(f"  ⚠ {os.path.basename(path)} 仍引用 {d}")
    print("自检通过：被删条目已无定义残留。")
    print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
