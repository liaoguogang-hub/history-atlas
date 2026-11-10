# -*- coding: utf-8 -*-
"""Patch summary lengths in spec2."""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_fig_expand_spec2.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

idx["fig-marie-curie"]["summary"] = "放射性元素的发现者，两度获诺贝尔奖，是近代物理与化学的奠基性人物。"
idx["fig-yuan-longping"]["summary"] = "杂交水稻的培育者，以显著提高稻谷产量而惠及全球数十亿人口的农学家。"
idx["fig-churchill"]["summary"] = "英国首相，以二战中拒绝和谈领导英国御敌，后并获诺贝尔文学奖。"

io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched")
