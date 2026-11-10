# -*- coding: utf-8 -*-
import io, re, sys
p = r"C:\Users\guoga\Documents\DSH\data\.tmp\fixperiods.py"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")
for i in (128, 129, 134, 135):
    L = lines[i]
    print("=== line", i + 1, "quotes:", L.count('"'))
    for m in re.finditer('"', L):
        print("   ", m.start(), repr(L[max(0, m.start()-20):m.start()+20]))
