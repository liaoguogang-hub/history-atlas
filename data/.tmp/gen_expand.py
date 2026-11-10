# -*- coding: utf-8 -*-
"""Build world_fig_expand1.json from a compact Python spec.

Every entry is written with full-width quotes only, so no JSON escaping
problems arise. This script also validates:
  - biography >= 380 chars
  - achievements >= 6
  - summary 30..60
  - no ASCII letters in summary/biography/achievements/quotes/tags/alias/role/lifeText
  - relatedFigures/relatedEvents ids exist in data/world.json
  - ids are unique and exist in data/world.json figures
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"

FIG_IDS = set()
EVT_IDS = set()
_periods = json.load(io.open(W, encoding="utf-8"))
for f in _periods["figures"]:
    FIG_IDS.add(f["id"])
for e in _periods["events"]:
    EVT_IDS.add(e["id"])
PER_IDS = {p["id"] for p in _periods["periods"]}

LATIN = re.compile(r"[A-Za-z]{2,}")

ENTRIES = json.load(io.open(os.path.join(TMP, "world_fig_expand_spec.json"), encoding="utf-8"))

problems = []
out = []
seen = set()
for e in ENTRIES:
    fid = e["id"]
    if fid in seen:
        problems.append(f"批内 id 重复: {fid}")
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
            v = str(e[k])
            s = max(0, m.start() - 25); t = min(len(v), m.end() + 25)
            problems.append(f"英文[{k}] {m.group(0)!r} in {fid}: …{v[s:t]}…")
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
    if "A-Za-z" in json.dumps(e, ensure_ascii=False):
        pass
    out.append(e)

path = os.path.join(TMP, "world_fig_expand1.json")
if problems:
    print(f"发现 {len(problems)} 个问题，未写出：")
    for p in problems:
        print("  " + p)
    sys.exit(1)

io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"已写出 {path}: {len(out)} 条")
