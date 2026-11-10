# -*- coding: utf-8 -*-
import io
p = r"C:\Users\guoga\Documents\DSH\data\.tmp\fixperiods.py"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")
L = lines[128]
print("LEN", len(L))
print("TAIL:", repr(L[-60:]))
print("chars 170-200:", [(i, L[i]) for i in range(170, min(200, len(L)))])
