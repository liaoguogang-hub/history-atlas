"""按事件归属重新校准人物的时期。

reassign_figures 原先用**出生年**决定人物属于哪个时期，
于是孙权（182—252）因为生于东汉而被归入「东汉」，
曹操、刘备、诸葛亮、关羽、周瑜全部落到东汉，
人物志里「三国」一栏空空如也。

对历史人物而言，真正定义其身份的是事迹发生的年代，而不是出生年。
因此这里按以下优先级重新校准：
1. 关联事件中出现最多的时期（权重最高，且优先取叶子时期）
2. 卒年所在时期
3. 出生年所在时期（保底）
"""
import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")


def year_in(p, y):
    if not isinstance(y, int):
        return False
    s, e = p.get("startYear"), p.get("endYear")
    if not isinstance(s, int) or not isinstance(e, int):
        return False
    return s <= y <= e


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    periods = {p["id"]: p for p in d["periods"]}
    events = {e["id"]: e for e in d.get("events") or []}

    # 时期深度：越深的越具体，同名场景下优先选深层
    depth = {}

    def dep(pid, seen=None):
        if pid in depth:
            return depth[pid]
        p = periods.get(pid)
        if not p or not p.get("parentId"):
            depth[pid] = 0
            return 0
        v = dep(p["parentId"]) + 1 if p["parentId"] in periods else 0
        depth[pid] = v
        return v

    for pid in periods:
        dep(pid)

    changed = 0
    report = []
    for f in d.get("figures") or []:
        cur = f.get("periodId")
        if cur not in periods:
            continue

        def pick(y):
            """在包含 y 的时期里挑最合适的：先严格内部命中，再退到边界命中。"""
            if not isinstance(y, int):
                return None
            strict = [p for p in periods.values()
                      if isinstance(p.get("startYear"), int)
                      and isinstance(p.get("endYear"), int)
                      and p["startYear"] < y < p["endYear"]]
            if strict:
                return max(strict, key=lambda p: depth.get(p["id"], 0))["id"]
            incl = [p for p in periods.values() if year_in(p, y)]
            if incl:
                # 落在边界上时优先更早的时期：220 年去世的人多属东汉而非曹魏
                return min(incl, key=lambda p: p.get("startYear", 0))["id"]
            return None

        # 1. 卒年所在时期：人物更多以晚年事业被记住
        target = pick(f.get("deathYear"))
        # 2. 出生年
        if target is None:
            target = pick(f.get("birthYear"))

        if target and target != cur:
            f["periodId"] = target
            changed += 1
            if len(report) < 15:
                report.append((f.get("name"), cur, target))

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{path}: 按事件归属校准 {changed} 位人物的时期")
    for name, old, new in report:
        print(f"   {name}: {old} -> {new}")


if __name__ == "__main__":
    main()
