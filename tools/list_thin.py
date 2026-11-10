import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
pmap = {p["id"]: p.get("name") for p in d["periods"]}

rows = []
for f in d["figures"]:
    bio = (f.get("biography") or "")
    if len(bio) >= 120:
        continue
    rows.append(f)

rows.sort(key=lambda f: (f.get("periodId") or "", f.get("id") or ""))
print(f"待补 {len(rows)} 条\n")
for f in rows:
    print(f"{f['id']:30s} | {str(f.get('name')):10s} | {str(f.get('role')):8s} | "
          f"{str(pmap.get(f.get('periodId'))):10s} | by={str(f.get('birthYear')):>6} "
          f"dy={str(f.get('deathYear')):>6} | {len(f.get('biography') or '')}字")
    print(f"    summary: {(f.get('summary') or '')[:70]}")
    print(f"    bio    : {(f.get('biography') or '')[:70]}")
