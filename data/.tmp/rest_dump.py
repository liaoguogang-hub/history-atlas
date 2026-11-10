import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(io.open("data/china.json", encoding="utf-8"))
by = {f["id"]: f for f in d["figures"]}
pm = {p["id"]: p.get("name") for p in d["periods"]}

# 1. 生平 <300 的全部
thin = [f for f in d["figures"] if len(f.get("biography") or "") < 300]
# 2. 生平够长但 achievements 为空
noach = [f for f in d["figures"] if len(f.get("biography") or "") >= 300 and not (f.get("achievements") or [])]

print("=== 生平<300 ===", len(thin))
print("=== 生平够长但成就为空 ===", len(noach))
for f in noach:
    print(f"  {f['id']} | {f.get('name')} | {len(f.get('biography') or '')} | {pm.get(f.get('periodId'))}")

want = [f["id"] for f in thin] + [f["id"] for f in noach]
print("\n=== 字段 ===")
for w in want:
    f = by[w]
    print(json.dumps({
        "id": f["id"], "name": f["name"], "alias": f.get("alias"),
        "role": f.get("role"), "birthYear": f.get("birthYear"),
        "deathYear": f.get("deathYear"), "gender": f.get("gender"),
        "periodId": f.get("periodId"), "blen": len(f.get("biography") or ""),
        "ach": len(f.get("achievements") or []),
    }, ensure_ascii=False))
