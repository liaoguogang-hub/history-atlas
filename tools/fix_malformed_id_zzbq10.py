# -*- coding: utf-8 -*-
"""修复世界史人物库中的两处畸形 id —— 直接改源分片，保证 build_data 重建后仍生效。

问题：
- fig-sherlock-plo  实为「薛西斯一世」（Sherlock 是误拼）
- fig-o-kongo       实为「织田信长」（o-kongo 疑为刚果误标）

只改 data/.tmp/world_*.json 分片：
  - 定义处（world_fig_*.json 里 "id": "old"）
  - 引用处（events 的 figures[] / figures 的 relatedFigures[] / periods 的 keyFigures[]）

安全措施：
  1. 改前断言该人物 name 与预期一致
  2. 改前断言新 id 不存在
  3. 改后断言所有分片里不再出现旧 id
  4. 支持 --dry-run

用法：
    python tools/fix_malformed_id_zzbq10.py [--dry-run]
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "data", ".tmp")

RENAMES = {
    "fig-sherlock-plo": ("fig-xerxes", "薛西斯"),
    "fig-o-kongo": ("fig-oda-nobunaga", "织田信长"),
}

SHARD_GLOB = os.path.join(TMP, "world_*.json")


def load_shards():
    shards = {}
    for p in sorted(glob.glob(SHARD_GLOB)):
        try:
            shards[p] = json.load(io.open(p, encoding="utf-8"))
        except Exception as exc:                     # noqa: BLE001
            print(f"  ! 跳过无法解析的分片 {os.path.basename(p)}: {exc}")
    return shards


def iter_records(obj):
    """分片可能是数组，也可能是 {events:...}/{figures:...}/{periods:...}。"""
    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                yield it
    elif isinstance(obj, dict):
        for key in ("events", "figures", "periods"):
            for it in obj.get(key) or []:
                if isinstance(it, dict):
                    yield it


# 引用字段可能是全称，也可能是缩写（world_events_b*.json / world_figures_core.json 用缩写）
REF_KEYS = (
    "figures", "relatedFigures", "keyFigures",   # 全称
    "f", "rf", "kf",                              # 缩写
)


def main():
    dry = "--dry-run" in sys.argv
    shards = load_shards()
    print(f"扫描 {len(shards)} 个世界史分片")

    # ---------- 前置校验 ----------
    for old, (new, expect) in RENAMES.items():
        found = None
        for path, obj in shards.items():
            for it in iter_records(obj):
                if it.get("id") == old:
                    found = (path, it)
                    break
            if found:
                break
        if not found:
            print(f"  ! 未在分片中找到 {old}（可能仅存在于已生成产物），跳过")
            continue
        path, rec = found
        name = rec.get("name", "")
        if expect not in name:
            raise SystemExit(
                f"中止：{old} 名称为「{name}」，与预期「{expect}」不符，拒绝改动。")
        # 新 id 冲突检查
        for obj in shards.values():
            for it in iter_records(obj):
                if it.get("id") == new:
                    raise SystemExit(f"中止：新 id {new} 已存在于分片中。")
        print(f"  ✓ {old} → {new}（名称「{name}」校验通过，定义于 {os.path.basename(path)}）")

    if dry:
        print("\n[dry-run] 未写入。")
        return

    # ---------- 执行替换 ----------
    total = 0
    for path, obj in shards.items():
        changed = 0
        for it in iter_records(obj):
            # 定义处
            old_id = it.get("id")
            if old_id in RENAMES:
                it["id"] = RENAMES[old_id][0]
                changed += 1
            # 引用处（含缩写键）
            for key in REF_KEYS:
                lst = it.get(key)
                if not isinstance(lst, list):
                    continue
                for i, v in enumerate(lst):
                    if v in RENAMES:
                        lst[i] = RENAMES[v][0]
                        changed += 1
        if changed:
            with io.open(path, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False, indent=1)
            print(f"  {os.path.basename(path)}: 修改 {changed} 处")
            total += changed

    # ---------- 后置自检 ----------
    for path in glob.glob(SHARD_GLOB):
        txt = io.open(path, encoding="utf-8").read()
        for old in RENAMES:
            if f'"{old}"' in txt:
                raise SystemExit(f"自检失败：{os.path.basename(path)} 仍残留 {old}")
    print(f"\n共修改 {total} 处，全部自检通过。")
    print("请运行 python tools/build_data.py 复核，并检查 WARN 数是否未上升。")


if __name__ == "__main__":
    main()
