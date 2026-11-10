# -*- coding: utf-8 -*-
"""清洗 figdata_*.json：移除控制字符，修正空 quotes 数组等。"""
import glob
import io
import json
import re

CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

for f in sorted(glob.glob("figdata_*.json")):
    raw = io.open(f, encoding="utf-8", newline="").read()
    fixed = CTRL.sub("", raw)
    if fixed != raw:
        io.open(f, "w", encoding="utf-8", newline="\n").write(fixed)
        print("cleaned control chars in", f)
    try:
        d = json.loads(fixed)
    except Exception as e:
        print("STILL BAD", f, e)
        continue
    # 修正 quotes 空串 -> 删除
    n = 0
    for p in d:
        qs = [q for q in p.get("q", []) if q and q.strip()]
        if len(qs) != len(p.get("q", [])):
            p["q"] = qs
            n += 1
    if n:
        io.open(f, "w", encoding="utf-8", newline="\n").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print("fixed %d empty quotes in %s" % (n, f))
    print("%-20s %d ok" % (f, len(d)))
