# -*- coding: utf-8 -*-
"""列出 periods.keyFigures 引用的全部 figure id，按时期分组。"""
import importlib.util
import collections

spec = importlib.util.spec_from_file_location("p", "periods_data.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = m.PERIODS

d = {}
for p in P:
    d.setdefault(p["id"], p)

groups = collections.OrderedDict()
for p in P:
    for f in (p.get("keyFigures") or []):
        groups.setdefault(p["id"], []).append(f)

allf = sorted({f for v in groups.values() for f in v})
print("TOTAL distinct figure refs:", len(allf))
print()
for pid, fs in groups.items():
    print("%-22s %s" % (pid, " ".join(fs)))
