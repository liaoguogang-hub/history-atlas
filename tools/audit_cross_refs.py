import io
import json
import os
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))

cn_figs = {f["id"]: f for f in china["figures"]}
w_fig_ids = {f["id"] for f in world["figures"]}

# 世界史里引用了哪些中国史人物
cross = collections.Counter()
where = collections.defaultdict(set)
for e in world["events"]:
    for fid in (e.get("figures") or []):
        if fid in cn_figs and fid not in w_fig_ids:
            cross[fid] += 1
            where[fid].add("event:" + e["id"])
for f in world["figures"]:
    for fid in (f.get("relatedFigures") or []):
        if fid in cn_figs and fid not in w_fig_ids:
            cross[fid] += 1
            where[fid].add("figure:" + f["id"])

print(f"world references {len(cross)} china figures not present in world")
for fid, n in cross.most_common(60):
    cn = cn_figs[fid]
    print(f"  {n:3d}x  {fid:28s} {cn.get('name')}  [{cn.get('role')}]  "
          f"period={cn.get('periodId')}  bio_len={len(cn.get('biography') or '')}")
