# -*- coding: utf-8 -*-
"""Final fixes: summary lengths and achievement counts."""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
SPEC_DIR = r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs"

SUMMARY = {
    "fig-voltaire": "法国启蒙运动的旗手，以讽刺作品与大量著述批判教会权威与政治专制。",
    "fig-nebuchadnezzar": "新巴比伦王朝的第二位君主，重建巴比伦城并毁灭耶路撒冷与圣殿。",
    "fig-solomon": "以色列的第三位国王，以智慧闻名并主持营建耶路撒冷圣殿与宫殿工程。",
    "fig-akhenaten": "古埃及第十八王朝法老，推行史上前所未有的唯一神阿顿崇拜改革。",
    "fig-marco-polo": "威尼斯商人与旅行家，其东方游记是欧洲人认知东方的最重要文本。",
}

EXTRA_ACH = {
    "fig-moses": ["成为三大宗教传统共享的先知形象，其事迹被反复重述与阐释"],
    "fig-solomon": ["与推罗的希兰建立贸易往来，其海港技艺是圣殿工程的重要依赖"],
    "fig-akhenaten": ["其改革引发的教权更迭成为研究古代宗教变迁的重要案例"],
}

for fn in sorted(os.listdir(SPEC_DIR)):
    path = os.path.join(SPEC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        if e["id"] in SUMMARY:
            e["summary"] = SUMMARY[e["id"]]; changed = True
        if e["id"] in EXTRA_ACH and len(e.get("achievements") or []) < 6:
            e["achievements"] = list(e["achievements"]) + EXTRA_ACH[e["id"]]
            changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "patched")
