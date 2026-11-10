import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1] if len(sys.argv) > 1 else "data/world.json"
d = json.load(io.open(path, encoding="utf-8"))
for p in d["periods"]:
    print(f"{p['id']:32s} parent={str(p.get('parentId')):24s} "
          f"{p.get('startYear')}..{p.get('endYear')}  {p.get('name')}")
