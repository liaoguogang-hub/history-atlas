# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs\b6.json"
d = json.load(io.open(P, encoding="utf-8"))
for x in d:
    if x["id"] == "fig-charles-ellington":
        x["summary"] = "英国陆军元帅与两度出任首相，以滑铁卢战役击败拿破仑而决定欧洲格局。"
io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("ok")
