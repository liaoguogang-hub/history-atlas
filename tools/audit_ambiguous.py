import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
pmap = {p["id"]: p.get("name") for p in d["periods"]}

groups = collections.defaultdict(list)
for f in d["figures"]:
    n = (f.get("name") or "").strip()
    if n:
        groups[n].append(f)

amb = []
for name, items in groups.items():
    if len(items) < 2:
        continue
    sigs = {(f.get("birthYear"), f.get("deathYear")) for f in items}
    if len(sigs) > 1:
        amb.append((name, items))

print(f"生卒年不一致的重名分组: {len(amb)}\n")
for name, items in amb:
    print(f"--- {name} ---")
    for f in items:
        print(f"   {f['id']:34s} by={str(f.get('birthYear')):>7} dy={str(f.get('deathYear')):>7} "
              f"period={str(f.get('periodId')):22s} bio={len(f.get('biography') or ''):4d}")
