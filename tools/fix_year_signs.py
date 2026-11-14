import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


SPLIT = re.compile(r"[－—–\-~至到]+")
TOK = re.compile(r"(公元前|公元|前)?\s*(\d+)\s*年")


def parse_one(seg, inherit_bc=False):
    """解析单侧年份片段，返回 (年, 是否有值)。

    inherit_bc: 该侧没有「公元前/公元」前缀时，是否沿用另一侧的纪元。
    形如 "公元1606年—1647年"，右侧 "1647年" 无前缀，
    应视作公元 1647 年（而不是解析失败）。
    """
    m = TOK.search(seg or "")
    if not m:
        return None, False
    n = int(m.group(2))
    prefix = m.group(1)
    if prefix in ("公元前", "前"):
        return -n, True
    if prefix == "公元":
        return n, True
    # 无前缀：沿用另一侧的纪元
    return (-n if inherit_bc else n), True


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
    # 先看左侧是否含「公元前」，用于决定右侧无前缀年份的纪元
    left_is_bc = "公元前" in (parts[0] or "") or (parts[0] or "").strip().startswith("前")
    by, ok1 = parse_one(parts[0])
    dy, ok2 = parse_one(parts[1], inherit_bc=left_is_bc)
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

        # 只在解析成功的一侧覆盖原值。
        # 旧实现无条件写回 (by, dy)，当 lifeText 只有一侧带「公元」前缀时
        # （如 "公元1606年—1647年"，右侧 1647 年没有前缀），
        # parse_one 返回 (None, False)，dy 为 None，
        # 于是把原本正确的 deathYear=1647 清成了 None。
        new_by = by if by is not None else r.get(bk)
        new_dy = dy if dy is not None else r.get(dk)

        if r.get(bk) != new_by or r.get(dk) != new_dy:
            fixed.append((r.get("id"), r.get(bk), r.get(dk), new_by, new_dy))
            r[bk], r[dk] = new_by, new_dy

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
