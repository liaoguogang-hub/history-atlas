import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
figs = d["figures"]
pmap = {p["id"]: p.get("name") for p in d["periods"]}

# 按「姓名 + 生卒年」聚类：同名且生卒年相同（或都为空）视为同一人
groups = collections.defaultdict(list)
for f in figs:
    key = (f.get("name") or "").strip()
    if not key:
        continue
    by, dy = f.get("birthYear"), f.get("deathYear")
    groups[key].append(f)

dupes = {k: v for k, v in groups.items() if len(v) > 1}
print(f"重名分组: {len(dupes)} 组，涉及 {sum(len(v) for v in dupes.values())} 条")

# 区分：同名但生卒年不同（可能是同名不同人）vs 完全重复
def sig(f):
    return (f.get("birthYear"), f.get("deathYear"))


real_dupe = 0
ambig = 0
for name, items in dupes.items():
    sigs = {sig(f) for f in items}
    if len(sigs) == 1:
        real_dupe += len(items) - 1
    else:
        ambig += len(items) - 1

print(f"  可合并（生卒年一致）: 多余的 {real_dupe} 条")
print(f"  生卒年不一致需人工判断: {ambig} 条")

print("\n=== 重复最多的 25 组 ===")
for name, items in sorted(dupes.items(), key=lambda kv: -len(kv[1]))[:25]:
    lens = [len(f.get("biography") or "") for f in items]
    print(f"  {name:10s} x{len(items)}  传记长度={lens}  ids={[f['id'] for f in items]}")

# 空传记
empty = [f for f in figs if not (f.get("biography") or "").strip()]
print(f"\n传记完全为空: {len(empty)} 条")
# 其中多少有同名伙伴可借内容
has_twin = 0
for f in empty:
    peers = [g for g in groups.get((f.get("name") or "").strip(), [])
             if g is not f and (g.get("biography") or "").strip()]
    if peers:
        has_twin += 1
print(f"  其中有同名伙伴可复用内容: {has_twin} 条")
print("  其余空传记 id:", " ".join(f["id"] for f in empty
                               if not any(g is not f and (g.get("biography") or "").strip()
                                          for g in groups.get((f.get("name") or "").strip(), []))))
