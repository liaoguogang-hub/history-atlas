# -*- coding: utf-8 -*-
import io, re
p = r"C:\Users\guoga\Documents\DSH\data\.tmp\fixperiods.py"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")
for i, L in enumerate(lines, 1):
    c = L.count('"')
    if c % 2 == 1:
        print("ODD line", i, "count", c)
        for m in re.finditer('"', L):
            print("   ", m.start(), repr(L[max(0, m.start()-30):m.start()+30]))
