"""检查事件年份是否被填成了所属时期的起始年（年份塌缩）。"""
import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    pm = {p["id"]: p for p in d["periods"]}

    collapsed = []
    for e in d["events"]:
        p = pm.get(e.get("periodId"))
        if not p:
            continue
        if e.get("year") == p.get("startYear"):
            collapsed.append(e)

    print(f"=== {sc} ===")
    print(f"  事件总数 {len(d['events'])}")
    print(f"  年份 == 时期起始年 的事件: {len(collapsed)} "
          f"({len(collapsed) * 100 // max(1, len(d['events']))}%)")

    by_period = collections.Counter(e["periodId"] for e in collapsed)
    print("  按时期分布（前 12）:")
    for pid, n in by_period.most_common(12):
        p = pm[pid]
        total = sum(1 for e in d["events"] if e.get("periodId") == pid)
        print(f"    {n:3d}/{total:3d}  {pid:24s} {p.get('name')}")

    # 同一时期里所有事件年份完全相同的，最可疑
    per = collections.defaultdict(list)
    for e in d["events"]:
        per[e.get("periodId")].append(e.get("year"))
    flat = []
    for pid, years in per.items():
        ys = [y for y in years if isinstance(y, int)]
        if len(ys) >= 3 and len(set(ys)) == 1:
            flat.append((pid, pm.get(pid, {}).get("name"), len(ys), ys[0]))
    print(f"  整个时期事件年份完全相同: {len(flat)} 个时期")
    for pid, name, n, y in sorted(flat, key=lambda x: -x[2])[:12]:
        print(f"    {n:3d}个事件全为 {y:>7}  {pid:24s} {name}")
    print()
