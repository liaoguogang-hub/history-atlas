import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1] if len(sys.argv) > 1 else "data/world.json"
d = json.load(io.open(path, encoding="utf-8"))
pmap = {p["id"]: p for p in d["periods"]}

bad_year = []
bad_end = []
for e in d["events"]:
    p = pmap.get(e.get("periodId"))
    if not p:
        continue
    ps, pe = p.get("startYear"), p.get("endYear")
    if not (isinstance(ps, int) and isinstance(pe, int)):
        continue
    y, ye = e.get("year"), e.get("yearEnd")
    if isinstance(y, int) and not (ps <= y <= pe):
        bad_year.append((e["id"], y, ps, pe, e.get("periodId"), e.get("name")))
    if isinstance(ye, int) and ye != y and not (ps <= ye <= pe):
        bad_end.append((e["id"], ye, ps, pe, e.get("periodId"), e.get("name")))

print(f"year outside   : {len(bad_year)}")
print(f"yearEnd outside: {len(bad_end)}")

for label, rows in (("YEAR", bad_year), ("YEAREND", bad_end)):
    if not rows:
        continue
    print(f"\n--- {label} ---")
    c = collections.Counter(x[4] for x in rows)
    for pid, n in c.most_common(10):
        p = pmap.get(pid, {})
        print(f"  {n:3d}  {pid:24s} [{p.get('startYear')}..{p.get('endYear')}] {p.get('name')}")
    for x in rows[:15]:
        print(f"    {x[0]:32s} y={x[1]:>7}  [{x[2]}..{x[3]}]  {x[5]}")
