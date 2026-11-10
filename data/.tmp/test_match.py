# -*- coding: utf-8 -*-
"""Simulate build_relations.py name matching for the new figures,
to verify the prose mentions will actually connect them to events/figures."""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
figs = {f["id"]: f for f in d["figures"]}
evs = {e["id"]: e for e in d["events"]}
pmap = {p["id"]: p for p in d["periods"]}

new = json.load(io.open(os.path.join(TMP, "world_fig_new2.json"), encoding="utf-8"))


def top_ancestor(pid):
    node = pmap.get(pid)
    seen = set()
    while node and node.get("parentId") and node["id"] not in seen:
        seen.add(node["id"])
        node = pmap.get(node.get("parentId"))
    return node["id"] if node else None


def name_ok(name):
    return isinstance(name, str) and len(name) >= 2 and re.search(r"[\u4e00-\u9fff]", name)


YEAR_GUARD = 400

print("=== 模拟：事件正文 → 新人物 ===")
hit_count = {}
for e in evs.values():
    text = (e.get("summary") or "") + (e.get("detail") or "")
    if not text:
        continue
    top = top_ancestor(e.get("periodId"))
    pool = [f for f in new]
    pool += [figs[f] for f in figs if f not in {n["id"] for n in new}]
    ev_year = e.get("year")
    for f in pool:
        nm = f.get("name")
        if not name_ok(nm):
            continue
        if isinstance(ev_year, int):
            fy = f.get("deathYear") if isinstance(f.get("deathYear"), int) else f.get("birthYear")
            if isinstance(fy, int) and abs(ev_year - fy) > YEAR_GUARD:
                continue
        if nm in text:
            hit_count.setdefault(f["id"], []).append(e["id"])

print("新人物被事件正文命中数：")
for f in new:
    hits = hit_count.get(f["id"], [])
    print("  %-26s %-12s 命中 %d 条: %s" % (
        f["id"], f["name"][:10], len(hits), ", ".join(hits[:5])))

print()
print("=== 模拟：人物正文 → 事件（同顶层祖先） ===")
for f in new:
    bio = (f.get("biography") or "") + (f.get("summary") or "")
    top = top_ancestor(f.get("periodId"))
    hits = []
    for e in evs.values():
        if top_ancestor(e.get("periodId")) != top:
            continue
        nm = e.get("name")
        if not name_ok(nm):
            continue
        if nm in bio:
            hits.append(e["id"])
    print("  %-26s %-12s 命中 %d 条: %s" % (
        f["id"], f["name"][:10], len(hits), ", ".join(hits[:6])))
