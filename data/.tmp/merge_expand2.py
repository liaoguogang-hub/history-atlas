# -*- coding: utf-8 -*-
"""Merge expansion spec files into data/.tmp/world_fig_expand2.json.

Specs live in data/.tmp/exp_specs/*.json so they can never collide with the
output file. Validation is strict:
  - id must exist in data/world.json figures
  - biography >= 380 chars
  - achievements >= 6
  - summary 30..60
  - NO ASCII letters anywhere in summary/biography/achievements/quotes/tags/alias/role/lifeText
  - relatedFigures / relatedEvents ids must exist in data/world.json
  - periodId must exist
"""
import glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SPEC_DIR = os.path.join(TMP, "exp_specs")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
LATIN = re.compile(r"[A-Za-z]{2,}")

os.makedirs(SPEC_DIR, exist_ok=True)
_world = json.load(io.open(W, encoding="utf-8"))
FIG_IDS = {f["id"] for f in _world["figures"]}
EVT_IDS = {e["id"] for e in _world["events"]}
PER_IDS = {p["id"] for p in _world["periods"]}

merged = []
for path in sorted(glob.glob(os.path.join(SPEC_DIR, "*.json"))):
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print(os.path.basename(path), "SKIP (parse error):", e)
        continue
    print(os.path.basename(path), "->", len(d))
    merged.extend(d)

problems = []
seen = set()
out = []
for e in merged:
    fid = e["id"]
    if fid in seen:
        problems.append(f"批内 id 重复: {fid}")
        continue
    seen.add(fid)
    if fid not in FIG_IDS:
        problems.append(f"id 不存在于 world.json: {fid}")
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
    out.append(e)

path = os.path.join(TMP, "world_fig_expand2.json")
if problems:
    print(f"\n发现 {len(problems)} 个问题，未写出：")
    for p in problems:
        print("  " + p)
    sys.exit(1)

io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\n已写出 {path}: {len(out)} 条")
