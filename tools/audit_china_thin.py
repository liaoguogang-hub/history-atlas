import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
pmap = {p["id"]: p.get("name") for p in d["periods"]}

# 自动补齐模板的几种典型形态
GENERIC = [
    "是这一时期的相关人物，其事迹见于此一时期的史籍记载",
    "是相关时期的重要人物，其生平与当时的社会变动紧密相系",
    "待补充条目",
]

thin = []
generic = []
real_short = []
for f in d["figures"]:
    bio = f.get("biography") or ""
    if len(bio) >= 120:
        continue
    is_gen = any(g in bio for g in GENERIC)
    row = (f["id"], f.get("name"), f.get("role"), f.get("periodId"),
           pmap.get(f.get("periodId")), len(bio), bio[:60])
    if is_gen:
        generic.append(row)
    else:
        real_short.append(row)

print(f"china figures <120字: {len(generic) + len(real_short)}")
print(f"  模板化占位: {len(generic)}")
print(f"  有真实内容但偏短: {len(real_short)}")

print("\n=== 模板化占位（按时期）===")
c = collections.Counter(x[4] for x in generic)
for k, v in c.most_common(20):
    print(f"  {v:4d}  {k}")

print("\n=== 模板化占位（按身份）===")
c2 = collections.Counter(x[2] for x in generic)
for k, v in c2.most_common(15):
    print(f"  {v:4d}  {k}")

print("\n=== 模板化占位 id 全表 ===")
print(" ".join(x[0] for x in generic))

print("\n=== 有真实内容但偏短（全部）===")
for x in real_short:
    print(f"  {x[0]:30s} {str(x[1]):10s} {str(x[2]):8s} {x[5]:3d}字 | {x[6]}")
