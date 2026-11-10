# -*- coding: utf-8 -*-
"""Diagnose JSON parse errors in a part file line by line."""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, sys.argv[1])
lines = io.open(P, encoding="utf-8").read().split("\n")
for i, L in enumerate(lines, 1):
    if not L.strip():
        continue
    t = L.rstrip().rstrip(",")
    try:
        json.loads(t)
    except Exception as e:
        print("LINE", i, "ERR:", e)
        print("   len", len(L))
        # show context around error column
        m = re.search(r"column (\d+)", str(e))
        if m:
            c = int(m.group(1))
            print("   ctx:", repr(L[max(0, c-120):c+120]))
        else:
            print("   head:", repr(L[:200]))
            print("   tail:", repr(L[-200:]))
