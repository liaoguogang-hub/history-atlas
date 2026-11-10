# -*- coding: utf-8 -*-
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs\a.json"
d = json.load(io.open(SRC, encoding="utf-8"))
for x in d:
    if x["id"] == "fig-w-gregory-i":
        x["summary"] = "罗马教皇，以编纂教令集与整顿教会行政重建了罗马教会的权威与秩序。"
io.open(SRC, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("ok")
