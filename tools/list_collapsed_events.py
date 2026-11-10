import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
pm = {p["id"]: p for p in d["periods"]}

groups = collections.defaultdict(list)
for e in d["events"]:
    p = pm.get(e.get("periodId"))
    if not p:
        continue
    if e.get("year") == p.get("startYear"):
        groups[p["id"]].append(e)

for pid in sorted(groups, key=lambda k: pm[k].get("startYear") or 0):
    p = pm[pid]
    print(f"\n## {p.get('name')} ({pid}) 起始年 {p.get('startYear')} 共 {len(groups[pid])} 条")
    for e in groups[pid]:
        print(f"  {e['id']:36s} {e.get('name')}")

# 同时列出重名事件
print("\n\n=== 重名事件 ===")
byname = collections.defaultdict(list)
for e in d["events"]:
    byname[e.get("name")].append(e["id"])
for n, ids in byname.items():
    if len(ids) > 1:
        print(f"  {n}: {ids}")
