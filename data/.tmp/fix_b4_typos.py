# -*- coding: utf-8 -*-
"""Fix JSON typos in exp_specs/b4.json:
   "name":"X",""alias":  ->  "name":"X","alias":
   "gender":"male",""summary" -> "gender":"male","summary"
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs\b4.json"
s = io.open(P, encoding="utf-8").read()

# generic: `,""key":` -> `,"key":`
s = re.sub(r',""(\w+)":', r',"\1":', s)
# generic: `{"` leftover
s = s.replace('{"', '{"')

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
try:
    d = json.load(io.open(P, encoding="utf-8"))
    print("parsed OK:", len(d))
except Exception as e:
    print("still broken:", e)
    for i, LL in enumerate(s.split("\n"), 1):
        t = LL.rstrip().rstrip(",")
        if not t.strip() or t in ("[", "]"):
            continue
        try:
            json.loads(t)
        except Exception as e2:
            m = re.search(r"column (\d+)", str(e2))
            c = int(m.group(1)) if m else 0
            print("  line", i, e2)
            print("   ctx:", repr(LL[max(0, c-120):c+120]))
