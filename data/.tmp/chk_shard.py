#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查分片：JSON 可解析、id 唯一、category 合法、periodId 存在、年份落在时期区间、f 引用的 figure 是否存在于已有分片或本批。"""
import json, sys, glob, io, os

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(D, "world_periods.json"), encoding="utf-8"))
PM = {p["id"]: p for p in P}

CATS = {"political","military","economic","cultural","scientific","social","religious","art",
        "literature","education","technology","exploration","conflict","treaty","reform","dynasty",
        "cross-civilization","disaster","health","economy-crisis"}

files = sys.argv[1:]
known_fig = set()
known_ev = set()
for f in glob.glob(os.path.join(D, "world_*.json")):
    try:
        raw = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(raw, list):
        continue
    for it in raw:
        if "role" in it or "ro" in it:
            known_fig.add(it["id"])
        elif "year" in it or "y" in it:
            known_ev.add(it["id"])

errs = []
new_fig = set()
new_ev = set()
for f in files:
    raw = json.load(open(f, encoding="utf-8"))
    for it in raw:
        eid = it.get("id")
        if eid in new_fig or eid in new_ev:
            errs.append(f"{f}: 重复 id {eid}")
        if "role" in it or "ro" in it:
            new_fig.add(eid)
        else:
            new_ev.add(eid)

for f in files:
    raw = json.load(open(f, encoding="utf-8"))
    for it in raw:
        eid = it.get("id")
        isfig = "role" in it or "ro" in it
        if isfig:
            pid = it.get("p") or it.get("periodId")
            if pid not in PM:
                errs.append(f"{eid}: periodId 不存在 {pid}")
            by = it.get("by", it.get("birthYear"))
            dy = it.get("dy", it.get("deathYear"))
            if by is not None and dy is not None and by > dy:
                errs.append(f"{eid}: birthYear > deathYear")
            if by == 0 or dy == 0:
                errs.append(f"{eid}: 年份为 0")
            s = it.get("s") or it.get("summary") or ""
            if not (10 <= len(s) <= 120):
                errs.append(f"{eid}: summary 长度 {len(s)}")
            b = it.get("bio") or it.get("biography") or ""
            if len(b) < 100:
                errs.append(f"{eid}: biography 长度 {len(b)}")
            for r in (it.get("re") or it.get("relatedEvents") or []):
                if r not in known_ev and r not in new_ev:
                    errs.append(f"{eid}: relatedEvents 悬空 {r}")
            for r in (it.get("rf") or it.get("relatedFigures") or []):
                if r not in known_fig and r not in new_fig:
                    errs.append(f"{eid}: relatedFigures 悬空 {r}")
            continue
        pid = it.get("p") or it.get("periodId")
        cat = it.get("c") or it.get("category")
        if cat not in CATS:
            errs.append(f"{eid}: category 非法 {cat}")
        if pid not in PM:
            errs.append(f"{eid}: periodId 不存在 {pid}")
        else:
            p = PM[pid]
            y = it.get("y", it.get("year"))
            ye = it.get("ye", it.get("yearEnd"))
            if y is not None and not (p["startYear"] <= y <= p["endYear"]):
                errs.append(f"{eid}: year {y} 不在 {pid}[{p['startYear']},{p['endYear']}]")
            if ye is not None and not (p["startYear"] <= ye <= p["endYear"]):
                errs.append(f"{eid}: yearEnd {ye} 不在 {pid}[{p['startYear']},{p['endYear']}]")
        imp = it.get("imp", it.get("importance"))
        if imp not in (1,2,3,4,5):
            errs.append(f"{eid}: importance 非法 {imp}")
        s = it.get("s") or it.get("summary") or ""
        if not (10 <= len(s) <= 120):
            errs.append(f"{eid}: summary 长度 {len(s)}")
        d = it.get("d") or it.get("detail") or ""
        if len(d) < 80:
            errs.append(f"{eid}: detail 长度 {len(d)}")
        for r in (it.get("f") or it.get("figures") or []):
            if r not in known_fig and r not in new_fig:
                errs.append(f"{eid}: figures 引用不存在的人物 {r}")

print(f"检查 {len(files)} 个分片")
if errs:
    print(f"ERROR {len(errs)}")
    for e in errs[:80]:
        print("  " + e)
    if len(errs) > 80:
        print(f"  ...另有 {len(errs)-80} 条")
    sys.exit(1)
print("OK 0 error")
