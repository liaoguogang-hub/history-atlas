import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


SPLIT = re.compile(r"[－—–\-~至到]+")
TOK = re.compile(r"(公元前|公元)\s*(\d+)\s*年")


def parse_one(seg):
    """解析单侧年份片段，返回 (年, 是否有值)。"""
    m = TOK.search(seg or "")
    if not m:
        return None, False
    n = int(m.group(2))
    return (-n if m.group(1) == "公元前" else n), True


def parse_lt(lt):
    """从 lifeText 解析 (生年, 卒年)。

    按分隔符切左右两侧分别解析，因此支持只有一侧的写法：
        "？－公元784年"   → (None, 784)
        "公元1963年－"    → (1963, None)
        "公元前1657年－公元前1700年" → (-1657, -1700)

    旧实现要求至少两个年份 token，「？－公元784年」这类只有一侧的
    条目会被整个跳过，导致 birthYear/deathYear 的符号错误无人纠正。
    """
    if not lt or "不详" in lt:
        return None
    parts = SPLIT.split(lt)
    if len(parts) < 2:
        return None
    by, ok1 = parse_one(parts[0])
    dy, ok2 = parse_one(parts[1])
    if not ok1 and not ok2:
        return None
    return by, dy


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))

    # 顶层可能是 scope 数据集（dict）或裸数组
    is_dataset = isinstance(data, dict)
    arr = (data.get("figures") or []) if is_dataset else data

    fixed = []
    for r in arr:
        if not isinstance(r, dict):
            continue
        lt = r.get("lifeText") or r.get("lt") or ""
        parsed = parse_lt(lt)
        if not parsed:
            continue
        by, dy = parsed
        bk = "birthYear" if "birthYear" in r else "by"
        dk = "deathYear" if "deathYear" in r else "dy"
        if r.get(bk) != by or r.get(dk) != dy:
            fixed.append((r.get("id"), r.get(bk), r.get(dk), by, dy))
            r[bk], r[dk] = by, dy

    if fixed:
        if is_dataset:
            data["figures"] = arr
            out = data
        else:
            out = arr
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(out, ensure_ascii=False, indent=1)
        )
    print(f"{path}: synced {len(fixed)} year pairs from lifeText")
    for f in fixed[:12]:
        print("   ", f)


if __name__ == "__main__":
    main()
