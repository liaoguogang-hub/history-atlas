"""校验人物扩充分片。

在把分片并入主数据之前，先检查下列问题：
1. 正文 / 摘要里混入英文单词或拉丁字母（中文史料里不该出现，
   常见的成因是撰写时手滑或从英文资料直译）。
2. 同一条记录里出现重复的 JSON 键（后写的会覆盖先写的，
   导致前面的内容被静默丢弃）。
3. 必需字段缺失、生平过短、成就条目过少。
4. id 重复（同一批里写了两遍）。
5. 引用的 relatedFigures / relatedEvents 是否存在。
"""
import io
import json
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

LATIN = re.compile(r"[A-Za-z]{2,}")
# 这些拉丁词在中文文本里是合法的（专有名词等），单独放行
ALLOW = {
    "MRI", "GDP", "GDP", "UNESCO", "DNA", "CPU", "PM", "AM",
}

REQUIRED = ("id", "name", "role", "summary", "biography", "periodId")

# 「补丁分片」模式：只带 id 与部分字段的批次（例如只补 achievements）。
# 用 --patch 开启，此时只校验已出现的字段，不要求条目完整。
PATCH = False


def check_shard(path, known_ids=None):
    raw = io.open(path, encoding="utf-8").read()
    data = json.loads(raw)

    # ---- 重复 JSON 键检查 ----
    dup_keys = []

    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                dup_keys.append(k)
            seen.add(k)
        return dict(pairs)

    json.loads(raw, object_pairs_hook=hook)

    problems = []
    ids = []
    for f in data:
        fid = f.get("id", "<无 id>")
        ids.append(fid)

        # 1. 英文污染
        for k in ("summary", "biography"):
            v = f.get(k) or ""
            for m in LATIN.finditer(v):
                word = m.group(0)
                if word in ALLOW:
                    continue
                s = max(0, m.start() - 22)
                e = min(len(v), m.end() + 22)
                problems.append(f"  [{k}] 英文片段 {word!r}: …{v[s:e]}…")
        for k in ("achievements", "quotes", "tags"):
            for it in (f.get(k) or []):
                for m in LATIN.finditer(str(it)):
                    word = m.group(0)
                    if word in ALLOW:
                        continue
                    problems.append(f"  [{k}] 英文片段 {word!r}: {it}")

        # 2. 必需字段
        if PATCH:
            # 补丁模式：至少要有 id 和一个可写字段
            if not f.get("id"):
                problems.append("  缺字段 id")
            writable = [k for k in ("biography", "summary", "achievements",
                                    "quotes", "role", "alias", "birthYear",
                                    "deathYear", "periodId", "gender", "tags",
                                    "relatedFigures", "relatedEvents")
                        if k in f]
            if not writable:
                problems.append("  没有任何可写字段")
        else:
            for k in REQUIRED:
                if not f.get(k):
                    problems.append(f"  缺字段 {k}")

        # 3. 长度（补丁模式下只检查已给出的字段）
        if "biography" in f:
            bio = len(f.get("biography") or "")
            if not PATCH and bio < 200:
                problems.append(f"  生平过短 {bio} 字")
        if "achievements" in f:
            ach = f.get("achievements") or []
            if not isinstance(ach, list):
                problems.append(f"  achievements 不是数组: {type(ach).__name__}")
            elif not PATCH and len(ach) < 3:
                problems.append(f"  成就过少 {len(ach)} 条")

    # 4. 批内 id 重复
    for i, fid in enumerate(ids):
        if ids.count(fid) > 1:
            problems.append(f"  批内 id 重复: {fid}")

    # 5. 引用存在性
    if known_ids is not None:
        for f in data:
            for r in (f.get("relatedFigures") or []):
                if r not in known_ids:
                    problems.append(f"  relatedFigures 指向不存在的 id: {r}")
            for r in (f.get("relatedEvents") or []):
                if r not in known_ids:
                    problems.append(f"  relatedEvents 指向不存在的 id: {r}")

    print(f"=== {path} ===")
    print(f"  条目 {len(data)}")
    if dup_keys:
        print(f"  ⚠ 重复 JSON 键: {sorted(set(dup_keys))}")
    if problems:
        print(f"  ✗ 发现 {len(problems)} 个问题：")
        for p in problems:
            print("   " + p)
    else:
        print("  ✓ 未发现问题")
    return problems


def main():
    global PATCH
    known = None
    args = sys.argv[1:]
    if args and args[0] == "--patch":
        PATCH = True
        args = args[1:]
    if args and args[0] == "--known":
        china = json.load(io.open("data/china.json", encoding="utf-8"))
        world = json.load(io.open("data/world.json", encoding="utf-8"))
        known = ({f["id"] for f in china["figures"]} |
                 {e["id"] for e in china["events"]} |
                 {f["id"] for f in world["figures"]} |
                 {e["id"] for e in world["events"]})
        args = args[1:]
    total = 0
    for p in args:
        total += len(check_shard(p, known))
    if total:
        sys.exit(1)


if __name__ == "__main__":
    main()
