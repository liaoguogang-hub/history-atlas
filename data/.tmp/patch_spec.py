# -*- coding: utf-8 -*-
"""Patch the spec file: fix summary lengths and Latin leaks."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_fig_expand_spec.json")

d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

idx["fig-huang-chong"]["summary"] = "宋代中层官僚的代表，其生平仅存零星记载，可据以考订宋代文官群体的真实生存状态。"
idx["fig-nehru"]["summary"] = "印度首任总理与不结盟运动的共同发起者，亚非国家在冷战格局中的重要政治领袖。"
idx["fig-zhu-pei"]["summary"] = "宋代文献中留名的士人之一，其零星记载补充了科举官僚群体的日常生存图景。"
idx["fig-sankara"]["summary"] = "印度教哲学的奠基者，不二论学派的开创者，其注释与论辩影响了整个南亚思想史。"
idx["fig-nagarjuna"]["summary"] = "大乘佛教中观学派的开创者，以缘起与空性论奠定中观哲学并影响东亚诸宗。"
idx["fig-nagarjuna"]["alias"] = "龙树、 Nagarjuna".replace(" Nagarjuna", "")
idx["fig-nagarjuna"]["alias"] = "龙树"

io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched", len(d))
