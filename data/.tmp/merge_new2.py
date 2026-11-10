# -*- coding: utf-8 -*-
"""Merge NEW figure shards into data/.tmp/world_fig_new2.json with strict validation.

relatedFigures / relatedEvents may cite ids that already exist in
data/world.json OR that are being created within this same batch.
"""
import glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SRC_DIR = os.path.join(TMP, "new_specs")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
LATIN = re.compile(r"[A-Za-z]{2,}")

os.makedirs(SRC_DIR, exist_ok=True)
_world = json.load(io.open(W, encoding="utf-8"))
FIG_IDS = {f["id"] for f in _world["figures"]}
EVT_IDS = {e["id"] for e in _world["events"]}
PER_IDS = {p["id"] for p in _world["periods"]}
REQUIRED = ["id", "name", "alias", "role", "birthYear", "deathYear", "gender",
            "periodId", "summary", "biography", "achievements", "quotes",
            "relatedFigures", "relatedEvents", "tags"]

merged = []
for path in sorted(glob.glob(os.path.join(SRC_DIR, "*.json"))):
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print(os.path.basename(path), "SKIP parse:", e)
        continue
    print(os.path.basename(path), "->", len(d))
    merged.extend(d)

BATCH_IDS = {e.get("id") for e in merged}
KNOWN_FIG = FIG_IDS | BATCH_IDS

problems = []
seen = set()
out = []
for e in merged:
    fid = e.get("id")
    if fid in seen:
        problems.append(f"批内 id 重复: {fid}")
        continue
    seen.add(fid)
    if not fid.startswith("fig-w-"):
        problems.append(f"id 必须以 fig-w- 开头: {fid}")
    if fid in FIG_IDS:
        problems.append(f"id 已存在于 world.json（不可重复建）: {fid}")
    for k in REQUIRED:
        if k not in e:
            problems.append(f"缺字段 {k}: {fid}")
    bio = e.get("biography") or ""
    if len(bio) < 380:
        problems.append(f"生平过短 {len(bio)}: {fid}")
    ach = e.get("achievements") or []
    if len(ach) < 6:
        problems.append(f"成就过少 {len(ach)}: {fid}")
    sm = e.get("summary") or ""
    if not (30 <= len(sm) <= 60):
        problems.append(f"摘要长度 {len(sm)}: {fid}")
    for k in ("summary", "biography", "alias", "role", "lifeText"):
        for m in LATIN.finditer(str(e.get(k) or "")):
            v = str(e[k]); s2 = max(0, m.start() - 25); t = min(len(v), m.end() + 25)
            problems.append(f"英文[{k}] {m.group(0)!r} in {fid}: …{v[s2:t]}…")
    for k in ("achievements", "quotes", "tags"):
        for it in (e.get(k) or []):
            for m in LATIN.finditer(str(it)):
                problems.append(f"英文[{k}] {m.group(0)!r} in {fid}: {it}")
    for r in (e.get("relatedFigures") or []):
        if r not in FIG_IDS:
            problems.append(f"relatedFigures 不存在: {r} (in {fid})")
    for r in (e.get("relatedEvents") or []):
        if r not in EVT_IDS:
            problems.append(f"relatedEvents 不存在: {r} (in {fid})")
    if e.get("periodId") not in PER_IDS:
        problems.append(f"periodId 不存在: {e.get('periodId')} (in {fid})")
    b, de = e.get("birthYear"), e.get("deathYear")
    if b is not None and de is not None and b > de:
        problems.append(f"生卒倒置: {fid} {b} {de}")
    if b == 0 or de == 0:
        problems.append(f"年份为 0: {fid}")
    # 只保留库中已存在的引用（Lead 要求：related id 必须是已存在的 id）
    e["relatedFigures"] = [r for r in (e.get("relatedFigures") or []) if r in FIG_IDS]
    e["relatedEvents"] = [r for r in (e.get("relatedEvents") or []) if r in EVT_IDS]
    out.append(e)

path = os.path.join(TMP, "world_fig_new2.json")
if problems:
    print(f"\n发现 {len(problems)} 个问题，未写出：")
    for p in problems:
        print("  " + p)
    sys.exit(1)

io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\n已写出 {path}: {len(out)} 条")
