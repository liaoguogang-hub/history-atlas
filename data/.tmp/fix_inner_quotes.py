# -*- coding: utf-8 -*-
"""Repair a part JSON file: convert inner ASCII double-quote pairs inside
JSON string values into full-width quotation marks, then verify parse."""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, sys.argv[1])
lines = io.open(P, encoding="utf-8").read().split("\n")
out = []
changed = 0
for L in lines:
    res = []
    inq = False
    j = 0
    n = len(L)
    while j < n:
        c = L[j]
        if c == '"':
            if inq:
                k = j + 1
                while k < n and L[k] in " \t":
                    k += 1
                if k < n and L[k] in ",}]:":
                    inq = False
                    res.append('"')
                else:
                    res.append("\u201d")
                    changed += 1
            else:
                inq = True
                res.append('"')
            j += 1
            continue
        res.append(c)
        j += 1
    out.append("".join(res))
s = "\n".join(out)
try:
    d = json.loads(s)
    print("PARSE OK after fix, entries:", len(d), "inner quotes converted:", changed)
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
except Exception as e:
    print("STILL BROKEN:", e)
    # find offending line
    for i, LL in enumerate(s.split("\n"), 1):
        t = LL.rstrip().rstrip(",")
        if not t.strip() or t in ("[", "]"):
            continue
        try:
            json.loads(t)
        except Exception as e2:
            print("  line", i, e2)
            m = re.search(r"column (\d+)", str(e2))
            if m:
                c = int(m.group(1))
                print("   ctx:", repr(LL[max(0, c-150):c+150]))
