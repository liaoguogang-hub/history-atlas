# -*- coding: utf-8 -*-
"""v2.2.0 批次2：合并重复人物（同一人、不同译名/不同 id）。

审计发现 5 组同一历史人物被定义为两个条目（生卒年完全相同、姓名互译）：

  fig-leibniz            戈特弗里德·莱布尼茨    │ fig-w-leibniz      莱布尼茨
  fig-jawaharlal-nehru   贾瓦哈拉尔·尼赫鲁      │ fig-nehru          尼赫鲁
  fig-ibn-majid          伊本·马吉德           │ fig-ahmad-ibn-majid 艾哈迈德·伊本·马吉德
  fig-john-wycliffe      约翰·威克里夫          │ fig-w-john-wycliffe 约翰·薄利丘
  fig-w-augustus-alt     屋大维               │ fig-augustus       奥古斯都

合并规则：保留「传记更长 + 被引用更多」的条目，把另一条的所有引用改指向保留者，
再删除冗余定义。保留者的 name 采用更准确的中文常用名（见 KEEP_NAME）。

★ 特别注意 fig-w-john-wycliffe 的 name 是「约翰·薄利丘」——
  这是英文 Wycliffe 的错误音译，明显是生成时产生的讹误。合并时应丢弃该名。

执行顺序（避免索引失效）：
  1) 收集全部源分片中的引用，改指向保留 id
  2) 按 id 精确删除冗余定义
  3) 自检：旧 id 不得残留
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "data", ".tmp")

# 删除 id : 保留 id（注意方向：键=将被删除的冗余 id，值=保留的权威 id）
MERGES = {
    "fig-leibniz": "fig-w-leibniz",
    "fig-jawaharlal-nehru": "fig-nehru",
    "fig-ibn-majid": "fig-ahmad-ibn-majid",
    "fig-w-john-wycliffe": "fig-john-wycliffe",
    "fig-w-augustus-alt": "fig-augustus",
    "fig-montezuma": "fig-moctezuma",
    "fig-zzbq9-montezuma": "fig-moctezuma",
}

# 保留条目的最终显示名（统一为更通行的中文译名）
KEEP_NAME = {
    "fig-leibniz": "莱布尼茨",
    "fig-nehru": "尼赫鲁",
    "fig-ibn-majid": "伊本·马吉德",
    "fig-john-wycliffe": "约翰·威克里夫",
    "fig-augustus": "奥古斯都",
    "fig-moctezuma": "蒙特祖玛二世",
}

# 引用字段（含缩写键）
REF_KEYS = ("figures", "relatedFigures", "keyFigures", "f", "rf", "kf")


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


def main():
    dry = "--dry-run" in sys.argv
    shards = sorted(glob.glob(os.path.join(HERE, "*.json")))
    # 只处理分片，排除生成脚本与中间产物
    shards = [p for p in shards
              if os.path.basename(p).startswith(("world_", "china_", "figdata_", "evdata_"))]

    changed_refs = 0
    removed = 0
    kept_names = {}

    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        changed = False

        # 1) 引用改指向
        for rec in iter_records(obj):
            for key in REF_KEYS:
                lst = rec.get(key)
                if not isinstance(lst, list):
                    continue
                new = []
                touched = False
                for v in lst:
                    if v in MERGES:
                        new.append(MERGES[v])
                        touched = True
                    else:
                        new.append(v)
                if touched:
                    # 去重保序
                    rec[key] = list(dict.fromkeys(new))
                    changed_refs += sum(1 for v in lst if v in MERGES)
                    changed = True
            # 保留者改名
            if rec.get("id") in KEEP_NAME:
                want = KEEP_NAME[rec["id"]]
                if rec.get("name") != want:
                    rec["name"] = want
                    kept_names[rec["id"]] = want
                    changed = True

        # 2) 删除冗余定义
        if isinstance(obj, list):
            before = len(obj)
            obj = [x for x in obj
                   if not (isinstance(x, dict) and x.get("id") in MERGES)]
            if len(obj) != before:
                removed += before - len(obj)
                changed = True

        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"引用改指向 {changed_refs} 处；删除定义 {removed} 条。")
    if kept_names:
        print(f"改名 {len(kept_names)} 个：")
        for pid, name in kept_names.items():
            print(f"  {pid} → {name}")

    if dry:
        print("[dry-run] 未写入。")
        return

    # 3) 自检
    problems = []
    for path in shards:
        try:
            txt = io.open(path, encoding="utf-8").read()
        except Exception:                              # noqa: BLE001
            continue
        for old in MERGES:
            if f'"{old}"' in txt:
                problems.append((os.path.basename(path), old))
    if problems:
        raise SystemExit(f"自检失败：仍有残留 {problems[:6]}")
    print("自检通过：冗余 id 已清除。")
    print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
