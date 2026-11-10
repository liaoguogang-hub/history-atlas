"""修正几个含义不清的人物 id。

背景：历史项目的分片是逐步积累的，早期有些 id 用字面音译取名，
后来才有了更准确的命名，于是同一 id 在不同分片里指向了不同的人：

- ``fig-lu-xun``   早期指周树人（鲁迅），现已由新分片改为陆逊（东吴名将）
- ``fig-lu-xun-2`` 早期指周树人（鲁迅），但这个 id 看起来仍像陆逊
- ``fig-zhu-yougui`` 名字是「朱温」（后梁太祖），但「朱友珪」才是其子

处理方式：把含义不清的 id 重命名为能自解释的形式，并同步更新
全部分片里的引用（relatedFigures / keyFigures / figures 等）。
"""
import io
import json
import os
import glob
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 旧 id → 新 id
# 注意：不要用「fig-li-siyuan」——那个 id 原本指唐高祖李渊（566–635），
# 李嗣源是后唐明宗（867–933），与李渊是两个人。两位都改成自解释的名字：
#   李渊  → fig-li-yuan
#   李嗣源 → fig-li-siyuan-tang
RENAME = {
    "fig-lu-xun-2": "fig-luxun-writer",    # 周树人（鲁迅），避免与陆逊混淆
    "fig-zhu-yougui": "fig-zhu-wen",        # 朱温（后梁太祖）
    "fig-liwang-yan": "fig-li-siyuan-tang",  # 李嗣源（后唐明宗）
    "fig-li-siyuan": "fig-li-yuan",          # 李渊（唐高祖）
}

# 这些 id 在各分片中的正确姓名，用于交叉核对
EXPECTED_NAME = {
    "fig-luxun-writer": "周树人",
    "fig-zhu-wen": "朱温",
    "fig-li-siyuan-tang": "李嗣源",
    "fig-li-yuan": "李渊",
}

LIST_FIELDS = ("relatedFigures", "keyFigures", "figures", "relatedEvents")


def walk(node, changed):
    """递归遍历 JSON 结构，替换 id 引用。"""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k == "id" and isinstance(v, str) and v in RENAME:
                node["id"] = RENAME[v]
                changed.add(v)
            elif k in LIST_FIELDS and isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, str) and item in RENAME:
                        v[i] = RENAME[item]
                        changed.add(item)
            else:
                walk(v, changed)
    elif isinstance(node, list):
        for item in node:
            walk(item, changed)


def main():
    shards = sorted(glob.glob("data/.tmp/*.json"))
    total_changed = set()
    touched = []

    for path in shards:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        changed = set()
        walk(d, changed)
        if changed:
            io.open(path, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=1))
            touched.append((os.path.basename(path), sorted(changed)))
            total_changed |= changed

    print(f"重命名 {len(RENAME)} 个 id")
    for old, new in RENAME.items():
        mark = "✓" if old in total_changed else "（未出现）"
        print(f"   {old:20s} → {new:22s} {mark}")
    print(f"\n改动 {len(touched)} 个分片：")
    for name, ids in touched:
        print(f"   {name:30s} {ids}")

    # 交叉核对：重命名后的条目姓名是否符合预期
    print("\n=== 核对重命名后的条目 ===")
    for path in shards:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else []
        for x in items:
            if isinstance(x, dict) and x.get("id") in EXPECTED_NAME:
                ok = "✓" if x.get("name") == EXPECTED_NAME[x["id"]] else "✗"
                print(f"   {ok} {x['id']:22s} name={x.get('name')}")


if __name__ == "__main__":
    main()
