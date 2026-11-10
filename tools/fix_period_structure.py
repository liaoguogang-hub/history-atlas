"""校正中国史时期树的史实结构。

修三类问题：
1. 「十国」被错放成顶层时期，与「五代十国」并列——它应当是五代十国的子时期。
   同时「五代十国」的区间只覆盖到 960 年，未含十国存续至 979 年的部分。
2. 宋、辽、金的起始年被统一写成 979（宋灭北汉），
   但北宋建立于 960 年、辽建于 916 年、金建于 1115 年。
3. 近代三个子时期之间 1927→1931 存在断层。

所有调整后都会校验「子时期是否落在父时期区间内」。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# (id, 新 parentId（None 表示不改）, 新 startYear（None 表示不改）, 新 endYear)
PERIOD_FIX = [
    # 五代十国整体应到 979 年（十国最后一个政权北汉灭亡）
    ("cn-wudai", None, 907, 979),
    # 十国挂到五代十国之下；与五代同期并存
    ("cn-wudai-south", "cn-wudai", 907, 979),
    # 宋辽金主线从北宋建立（960）算起
    ("cn-song-liao-jin", None, 960, None),
    # 北宋建立于 960，不是 979
    ("cn-song-north", None, 960, None),
    # 辽建于 916
    ("cn-liao", None, 916, None),
    # 金建于 1115
    ("cn-jin", None, 1115, None),
    # 消除近代 1927→1931 断层
    ("cn-modern-republic", None, None, 1931),
]


def fmt(y):
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    by_id = {p["id"]: p for p in d["periods"]}

    changed = []
    for pid, new_parent, new_start, new_end in PERIOD_FIX:
        p = by_id.get(pid)
        if p is None:
            continue
        touched = False
        if new_parent is not None and p.get("parentId") != new_parent:
            p["parentId"] = new_parent
            touched = True
        if new_start is not None and p.get("startYear") != new_start:
            p["startYear"] = new_start
            p["startDateText"] = fmt(new_start)
            touched = True
        if new_end is not None and p.get("endYear") != new_end:
            p["endYear"] = new_end
            p["endDateText"] = fmt(new_end)
            touched = True
        if touched:
            changed.append(f"{pid}[{p.get('startYear')}..{p.get('endYear')}]"
                           f" parent={p.get('parentId')}")

    # 父时期必须覆盖全部子时期
    fixed_parents = []
    for p in list(by_id.values()):
        node = p
        seen = set()
        while node is not None and node["id"] not in seen:
            seen.add(node["id"])
            par = by_id.get(node.get("parentId"))
            if par is None:
                break
            grew = False
            if p["startYear"] < par["startYear"]:
                par["startYear"] = p["startYear"]
                par["startDateText"] = fmt(par["startYear"])
                grew = True
            if p["endYear"] > par["endYear"]:
                par["endYear"] = p["endYear"]
                par["endDateText"] = fmt(par["endYear"])
                grew = True
            if grew:
                fixed_parents.append(par["id"])
            node = par

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))

    print(f"{path}: 调整 {len(changed)} 个时期")
    for c in changed:
        print(f"   {c}")
    if fixed_parents:
        print(f"  父时期区间随之扩展: {sorted(set(fixed_parents))}")


if __name__ == "__main__":
    main()
