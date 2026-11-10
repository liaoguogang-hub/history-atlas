import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
pm = {p["id"]: p for p in d["periods"]}

rows = []
for e in d["events"]:
    p = pm.get(e.get("periodId"))
    if not p:
        continue
    if e.get("year") == p.get("startYear"):
        rows.append((e["id"], e.get("name"), e.get("year"), p.get("name")))

print(f"共 {len(rows)} 条\n")
for i, r in enumerate(sorted(rows, key=lambda x: (x[2] or 0))):
    print(f"{i+1:3d} {r[0]:38s} y={r[2]:>7} [{r[3]}] {r[1]}")
