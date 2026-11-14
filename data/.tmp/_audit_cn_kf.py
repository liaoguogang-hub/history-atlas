# -*- coding: utf-8 -*-
"""审计中国史各时期的 keyFigures 是否与其时代区间相符。

判据：人物的「主要活动期」（生年+25 至卒年）与该时期区间应有重叠。
若无重叠，则该人物大概率错挂。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

c = json.load(io.open("data/china.json", encoding="utf-8"))
pm = {p["id"]: p for p in c["periods"]}
fg = {f["id"]: f for f in c["figures"]}

print("中国史: %d 时期 / %d 事件 / %d 人物" % (
    len(c["periods"]), len(c["events"]), len(c["figures"])))
print()

issues = []
for p in c["periods"]:
    kf = p.get("keyFigures") or []
    if not kf:
        continue
    lo, hi = p.get("startYear"), p.get("endYear")
    if not isinstance(lo, int) or not isinstance(hi, int):
        continue
    for fid in kf:
        f = fg.get(fid)
        if not f:
            continue
        by, dy = f.get("birthYear"), f.get("deathYear")
        if not isinstance(by, int):
            continue
        dy = dy if isinstance(dy, int) else by
        mature = by + 20
        # 主要活动期 [mature, dy] 与 [lo, hi] 是否有交集
        if dy < lo or mature > hi:
            issues.append((p["id"], p.get("name", ""), f["name"], by, dy, lo, hi))

print("=== 中国史 keyFigures 中时代不符的人物: %d ===" % len(issues))
for pid, pname, fname, by, dy, lo, hi in issues:
    print("  %-22s %-12s %-10s %s~%s  时期(%s,%s)" % (pid, pname[:10], fname, by, dy, lo, hi))
