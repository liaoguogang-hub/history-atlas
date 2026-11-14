# -*- coding: utf-8 -*-
"""v2.6.0 批次3：合并中国史中同一人的重复条目。

审计发现 4 组同一人物重复定义（生卒年完全相同，姓名是本名与庙号/帝号之别）：

  fig-liang-wudi (梁武帝) ↔ fig-xiao-yan (萧衍)          464-549  同一人
  fig-kangxi (玄烨)     ↔ fig-zzbq2-kangxi (康熙帝)     1654-1722 同一人
  fig-qianlong (弘历)   ↔ fig-zzbq2-qianlong (乾隆帝)   1711-1799 同一人
  fig-liu-zongyuan (刘宗元) ↔ fig-liu-zongyuan-2 (柳宗元) 773-819 同一人
                          ↑ 前者「刘宗元」是姓氏笔误，应为「柳宗元」

合并规则：保留传记更长、引用更多的条目，统一采用通行名（保留者改名），
把另一条的所有引用指向保留者，再删除冗余定义。

★ 注意「玄烨/弘历/萧衍」是本名，「康熙帝/乾隆帝/梁武帝」是帝号——
  App 中显示帝号更符合用户认知，因此保留者采用帝号名。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "data", ".tmp")

# 删除 id : 保留 id
MERGES = {
    "fig-xiao-yan": "fig-liang-wudi",
    "fig-kangxi": "fig-zzbq2-kangxi",
    "fig-qianlong": "fig-zzbq2-qianlong",
    "fig-liu-zongyuan": "fig-liu-zongyuan-2",
}

# 保留条目的最终名字
KEEP_NAME = {
    "fig-liang-wudi": "梁武帝",
    "fig-zzbq2-kangxi": "康熙帝",
    "fig-zzbq2-qianlong": "乾隆帝",
    "fig-liu-zongyuan-2": "柳宗元",
}

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

    patterns = ["figdata_*.json", "china_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    refs = 0
    removed = 0
    renamed = 0

    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        changed = False

        # 1) 引用改指向 + 改保留者名
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
                    rec[key] = list(dict.fromkeys(new))
                    refs += sum(1 for v in lst if v in MERGES)
                    changed = True
            if rec.get("id") in KEEP_NAME:
                want = KEEP_NAME[rec["id"]]
                if rec.get("name") != want:
                    rec["name"] = want
                    renamed += 1
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

    print("引用改指向 %d 处；删除定义 %d 条；改名 %d 个。" % (refs, removed, renamed))
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
        raise SystemExit("自检失败：仍有残留 %s" % problems[:6])
    print("自检通过：冗余 id 已清除。")
    print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
