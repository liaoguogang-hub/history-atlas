# -*- coding: utf-8 -*-
"""v1.9.0 数据修复：三项结构性问题。

【问题3】世界史 w-world-wars 里错挂了 4 条中国史事件
  ev-1919-may-fourth    五四运动与新文化运动的影响   → 中国史已有 ev-modern-may-fourth
  ev-may-fourth-detail  马克思主义传播与中共早期活动  → 中国史已有 ev-modern-communist-party
  ev-mao-longmarch      长征与遵义会议                 → 中国史已有 ev-zzbq2-changzheng / ev-zzbq2-zunyi
  ev-yanan              延安整风与延安精神             → 中国史无对应（属中国史内容，不应在世界史）
  处理：从世界史分片移除；其人物引用改指向中国史对应事件的说明不跨 scope，
        故直接清理引用后删除。

【问题1】13 个事件 id 在中国史与世界史中重复、但内容不同
  这些世界史条目本质是「从世界史视角复述中国史事件」，与 scope 内其他事件重复。
  处理：给世界史侧加 w- 前缀命名空间，避免 id 冲突；同时修所有引用。

【问题2】世界史人物补强（另由 _gen_zzbq12.py 生成新事件/人物）

用法：python tools/fix_scope_collision_zzbq12.py [--dry-run]
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "data", ".tmp")

WORLD_SHARDS = [os.path.join(TMP, "world_*.json")]

# ---- 问题3：从世界史移除的中国史错挂条目 ----
DROP_FROM_WORLD = {
    "ev-1919-may-fourth": "五四运动与新文化运动的影响",
    "ev-may-fourth-detail": "马克思主义的传播与中国共产党的早期活动",
    "ev-mao-longmarch": "长征与遵义会议",
    "ev-yanan": "延安整风与延安精神",
}

# ---- 问题1：跨 scope 冲突 id 改名（仅世界史侧） ----
# 世界史条目 -> 新 id（加 w- 命名空间前缀，语义保持）
RENAME_IN_WORLD = {
    "ev-qin-unify": "ev-w-qin-unify",
    "ev-han-founding": "ev-w-han-founding",
    "ev-han-wudi": "ev-w-han-wudi",
    "ev-han-zhangqian": "ev-w-han-zhangqian",
    "ev-han-buddhism": "ev-w-han-buddhism",
    "ev-tang-anlushan": "ev-w-tang-anlushan",
    "ev-tang-xuanzang": "ev-w-tang-xuanzang",
    "ev-song-wanyan": "ev-w-song-wanyan",
    "ev-yuan-founding": "ev-w-yuan-founding",
    "ev-ming-founding": "ev-w-ming-founding",
    "ev-ming-zhenghe": "ev-w-ming-zhenghe",
    "ev-ming-wanli": "ev-w-ming-wanli",
    "ev-qing-kangxi": "ev-w-qing-kangxi",
}


def load(patterns):
    out = {}
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            try:
                out[p] = json.load(io.open(p, encoding="utf-8"))
            except Exception as exc:                  # noqa: BLE001
                print(f"  ! 跳过 {os.path.basename(p)}: {exc}")
    return out


def iter_all(obj):
    """遍历分片中的全部记录（兼容数组 / 字典 / 缩写键）。"""
    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                yield it
    elif isinstance(obj, dict):
        for key in ("events", "figures", "periods"):
            for it in obj.get(key) or []:
                if isinstance(it, dict):
                    yield it


REF_KEYS = ("figures", "relatedEvents", "relatedFigures", "keyFigures",
            "f", "rf", "kf", "re")


def main():
    dry = "--dry-run" in sys.argv
    shards = load(WORLD_SHARDS)
    print(f"扫描 {len(shards)} 个世界史分片")

    actions = {"drop": 0, "rename": 0, "ref": 0}

    for path, obj in shards.items():
        changed = False

        # 顶层为数组时，直接按索引删除
        if isinstance(obj, list):
            # 先处理数组内的记录
            for it in obj:
                if not isinstance(it, dict):
                    continue
                rid = it.get("id")
                # 问题3：标记删除
                if rid in DROP_FROM_WORLD:
                    it["__drop__"] = True
                    changed = True
                    actions["drop"] += 1
                # 问题1：改名
                elif rid in RENAME_IN_WORLD:
                    it["id"] = RENAME_IN_WORLD[rid]
                    changed = True
                    actions["rename"] += 1

            # 引用替换
            for it in obj:
                if not isinstance(it, dict):
                    continue
                for key in REF_KEYS:
                    lst = it.get(key)
                    if not isinstance(lst, list):
                        continue
                    for i, v in enumerate(lst):
                        if v in RENAME_IN_WORLD:
                            lst[i] = RENAME_IN_WORLD[v]
                            actions["ref"] += 1
                            changed = True

            # 真正删除
            keep = [x for x in obj if not (isinstance(x, dict) and x.get("__drop__"))]
            if len(keep) != len(obj):
                obj[:] = keep
                changed = True

        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False, indent=1)
            print(f"  {os.path.basename(path)}: 已更新")

    # ---- 清理指向已删条目的悬空引用 ----
    if not dry:
        for path, obj in load(WORLD_SHARDS).items():
            changed = False
            for it in iter_all(obj):
                for key in REF_KEYS:
                    lst = it.get(key)
                    if not isinstance(lst, list):
                        continue
                    kept = [v for v in lst if v not in DROP_FROM_WORLD]
                    if len(kept) != len(lst):
                        it[key] = kept
                        actions["ref"] += len(lst) - len(kept)
                        changed = True
            if changed:
                with io.open(path, "w", encoding="utf-8") as fh:
                    json.dump(obj, fh, ensure_ascii=False, indent=1)

    print(f"\n删除 {actions['drop']} 条、改名 {actions['rename']} 条、"
          f"引用处理 {actions['ref']} 处")

    if dry:
        print("[dry-run] 未写入。")
        return

    # ---- 自检 ----
    problems = []
    for path in glob.glob(WORLD_SHARDS[0]):
        txt = io.open(path, encoding="utf-8").read()
        for old in DROP_FROM_WORLD:
            if f'"{old}"' in txt:
                problems.append((os.path.basename(path), "仍未删除", old))
        for old in RENAME_IN_WORLD:
            if f'"{old}"' in txt:
                problems.append((os.path.basename(path), "仍残留旧id", old))
    if problems:
        raise SystemExit(f"自检失败: {problems[:6]}")
    print("自检通过：错挂条目已删、冲突 id 已改名。")
    print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
