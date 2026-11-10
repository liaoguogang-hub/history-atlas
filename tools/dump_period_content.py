import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1] if len(sys.argv) > 1 else "data/world.json"
d = json.load(io.open(path, encoding="utf-8"))
target = sys.argv[2] if len(sys.argv) > 2 else "w-korea"

pmap = {p["id"]: p.get("name") for p in d["periods"]}

print(f"=== events in {target} ({pmap.get(target)}) ===")
for e in d["events"]:
    if e.get("periodId") == target:
        print(f"  {e['id']:34s} {e.get('year'):>7}  {e.get('name')}")

print(f"\n=== figures in {target} ===")
for f in d["figures"]:
    if f.get("periodId") == target:
        ph = "PH" if "待补充条目" in (f.get("biography") or "") else "  "
        print(f"  {f['id']:34s} {ph}  {f.get('name')}")
