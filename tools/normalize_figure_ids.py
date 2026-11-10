"""把含义不清或错配的人物 id 规范化为自解释的名字。

背景：分片是长期积累的，早期条目用简写或音译取 id，随着内容增补，
同一个 id 往往在不同分片里被复用于不同的人。李氏家族尤其集中——
库里有 40 多位姓李的人物，``fig-li-yuan`` / ``fig-li-yuan-2`` /
``fig-li-shimin`` / ``fig-li-shimin-2`` 这类 id 已经互相覆盖。

处理原则：
1. id 必须能自解释：包含姓名全称，必要时加朝代或身份加以区分。
2. 重命名必须**同步更新所有分片里的引用**，包括 relatedFigures / keyFigures。
3. 改完必须与 ``data/*.json`` 的实际姓名交叉核对，防止把 A 的 id 挂到 B 身上。

本脚本是幂等的：已经改名过的条目不会被再次改动。
"""
import io
import json
import os
import glob
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 旧 id → (新 id, 期望的姓名)
# 新 id 必须全局唯一，且能自解释。
# 旧 id → (新 id, 期望的姓名)
# 新 id 必须全局唯一，且能自解释。
#
# 有些 id 在不同分片里指向过不同的人（同姓同字、或张冠李戴），
# 光看 id 无法区分，必须同时核对记录里的姓名。
# 因此下面用 (旧 id, 记录里的姓名) → (新 id) 的精确匹配。
#
# 注意 fig-li-chen 这一对：分片里原本用 fig-li-chen 指唐哀宗李柷，
# 而另一条分片用 fig-tang-ai-di 指李艾。统一为：
#   李柷 → fig-li-zhu
#   李艾 → fig-li-ai
RENAME_BY_ID_AND_NAME = {
    # ---- 鲁迅 / 陆逊 ----
    ("fig-lu-xun-2", "周树人"): "fig-luxun-writer",
    ("fig-lu-xun-2", "鲁迅"): "fig-luxun-writer",
    # ---- 朱温（后梁太祖） ----
    ("fig-zhu-yougui", "朱温"): "fig-zhu-wen",
    ("fig-zhu-yougui", "朱全忠"): "fig-zhu-wen",
    # ---- 唐高祖李渊 ----
    ("fig-li-yuan-2", "李渊"): "fig-li-yuan-tang",
    # ---- 唐太宗李世民 ----
    ("fig-li-shimin-2", "李世民"): "fig-li-shimin-tang",
    # ---- 唐哀宗李柷 ----
    ("fig-li-chen", "李柷"): "fig-li-zhu",
    ("fig-tang-ai-di-2", "李柷"): "fig-li-zhu",
    # ---- 后唐明宗李嗣源 ----
    ("fig-liwang-yan", "李嗣源"): "fig-li-siyuan-tang",
    # ---- 唐代宗时期将领李艾 ----
    ("fig-tang-ai-di", "李艾"): "fig-li-ai",
    ("fig-li-zhu", "李艾"): "fig-li-ai",
    # ---- 后唐庄宗李从厚 ----
    ("fig-li-chang-tang", "李从厚"): "fig-li-conghou",
    # ---- 后唐末帝李昶 ----
    ("fig-li-yan-hao", "李昶"): "fig-li-chang-tang",
    ("fig-li-chang-tang", "李昶"): "fig-li-chang-tang",
}

# 兜底：只按 id 改名（该 id 在所有分片里都指向同一个人）
RENAME = {
    "fig-li-siyuan": "fig-li-yuan",          # 李渊
    "fig-li-conghou": "fig-li-conghou",      # 占位，避免误判
}

# 新 id → 期望姓名（用于最终核对）
EXPECTED_NAME = {
    "fig-luxun-writer": "周树人",
    "fig-zhu-wen": "朱温",
    "fig-li-yuan-tang": "李渊",
    "fig-li-shimin-tang": "李世民",
    "fig-li-zhu": "李柷",
    "fig-li-ai": "李艾",
    "fig-li-siyuan-tang": "李嗣源",
    "fig-li-conghou": "李从厚",
    "fig-li-chang-tang": "李昶",
}

LIST_FIELDS = ("relatedFigures", "keyFigures", "figures")


def _target_for(old_id, name):
    """算出这条记录应该改名成什么。

    优先用 (旧 id, 姓名) 的精确匹配；没有匹配项时，
    再退回只按 id 的映射。
    """
    if name:
        t = RENAME_BY_ID_AND_NAME.get((old_id, name))
        if t:
            return t
    return RENAME.get(old_id)


def walk(node, changed):
    """递归遍历 JSON 结构，替换 id 引用。

    只替换**引用字段**（relatedFigures 等）里的裸 id——
    那些引用没有姓名信息，只能按 id 替换。
    条目自身的 id 则要结合姓名判断。
    """
    if isinstance(node, dict):
        own_name = node.get("name") or node.get("n")
        for k, v in list(node.items()):
            if k == "id" and isinstance(v, str):
                tgt = _target_for(v, own_name)
                if tgt and tgt != v:
                    node["id"] = tgt
                    changed.add(v)
            elif k in LIST_FIELDS and isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, str):
                        # 引用字段按 id 替换（无姓名可用）
                        tgt = RENAME.get(item) or _id_only_targets().get(item)
                        if tgt and tgt != item:
                            v[i] = tgt
                            changed.add(item)
            else:
                walk(v, changed)
    elif isinstance(node, list):
        for item in node:
            walk(item, changed)


_ID_ONLY_CACHE = None


def _id_only_targets():
    """所有可能的旧 id → 新 id（忽略姓名），用于替换裸引用。"""
    global _ID_ONLY_CACHE
    if _ID_ONLY_CACHE is None:
        m = {}
        for (old, _name), new in RENAME_BY_ID_AND_NAME.items():
            m.setdefault(old, new)
        m.update(RENAME)
        _ID_ONLY_CACHE = m
    return _ID_ONLY_CACHE


def main():
    shards = sorted(glob.glob("data/.tmp/*.json"))

    print("=== 冲突检查 ===")
    # 判断依据是「改名完成后的稳态」：算出每条记录的最终 id，
    # 统计同一个最终 id 下聚集了哪些不同姓名。
    # 若同一最终 id 对应多个不同姓名，说明两条记录真的撞车了。
    final_owner = {}
    clash = False
    for path in shards:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else sum(
            [v for v in d.values() if isinstance(v, list)], [])
        for x in items:
            if not isinstance(x, dict) or not isinstance(x.get("id"), str):
                continue
            old = x["id"]
            nm = x.get("name") or x.get("n")
            final = old
            for _ in range(5):
                nxt = _target_for(final, nm if final == old else None)
                if not nxt or nxt == final:
                    break
                final = nxt
            if final != old:
                prev = final_owner.setdefault(final, set())
                if nm and prev and nm not in prev:
                    print(f"   ✗ {final} 将合并多个姓名: {sorted(prev)} ∪ {{'{nm}'}} "
                          f"（来自 {old}）")
                    clash = True
                elif nm:
                    prev.add(nm)
    if not clash:
        print("   全部新 id 无冲突")

    changed_files = []
    total = set()
    for path in shards:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        changed = set()
        # 改名可能是链式的，反复处理直到不再有变化
        for _ in range(5):
            before = len(changed)
            walk(d, changed)
            if len(changed) == before:
                break
        if changed:
            io.open(path, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=1))
            changed_files.append((os.path.basename(path), sorted(changed)))
            total |= changed

    print(f"\n=== 已改名 {len(total)} 处 ===")
    for name, ids in changed_files:
        print(f"   改动 {name:28s} {ids}")

    print("\n=== 核对合并结果 ===")
    for scope in ("china", "world"):
        p = f"data/{scope}.json"
        if not os.path.exists(p):
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        by_id = {f["id"]: f for f in d["figures"]}
        for new, expect in EXPECTED_NAME.items():
            f = by_id.get(new)
            if not f:
                print(f"   ✗ {new:24s} 不存在")
            else:
                ok = "✓" if f.get("name") == expect else "✗"
                print(f"   {ok} {new:24s} name={f.get('name')} "
                      f"生年={f.get('birthYear')} 生平={len(f.get('biography') or '')}字")


if __name__ == "__main__":
    main()
