# -*- coding: utf-8 -*-
"""Auto-fix Latin words in new-figure specs; also fix summary lengths."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SRC_DIR = os.path.join(TMP, "new_specs")

DICT = {
    "Letters": "书信集", "homeland": "祖国", "Claudius": "克劳狄乌斯",
    "debasement": "减成", "Galba": "加尔巴", "capturing了": "并夺取了",
    "capturing": "夺取", "Select": "行军", "Baia": "拜亚", "spectacula": "角斗表演",
    "Caesar": "凯撒", "purely": "纯粹的", "crown": "王冠", "home land": "祖国",
    "Anatomy": "解剖学", "Seneca": "塞涅卡", "Hadrian": "哈德良",
    "Trajan": "图拉真", "Commodus": "康茂德", "Diocletian": "戴克里先",
    "Charlemagne": "查理曼", "Petrarch": "彼特拉克", "Dante": "但丁",
    "Giotto": "乔托", "Aquinas": "阿奎那", "Bacon": "培根",
    "Ibn Rushd": "伊本·鲁希德", "Ibn Sina": "伊本·西那",
}

SUMMARY = {
    "fig-w-diocletian": "罗马末期的皇帝，以四帝共治与税制军制改革重建了帝国秩序。",
    "fig-w-gregory-i": "罗马教皇，以编纂教令集与整顿教会行政重建了罗马教会的权威。",
    "fig-w-nero": "罗马第五位皇帝，在位期间以暴政与角斗士身份著称，最终在反乱中自杀。",
    "fig-w-trajan": "罗马帝国鼎盛期的皇帝，以最大疆域与行省的经营及公共工程著称。",
    "fig-w-hadrian": "罗马皇帝，以巩固边疆、行省巡行与哈德良长城重塑了帝国的防御。",
    "fig-w-commodus": "罗马帝国末期的皇帝，以角斗士身份与暴政著称，统治后帝国陷入内乱。",
    "fig-w-cicero": "罗马最杰出的演说家与政治家，以拉丁散文的典范与共和理想的表达著称。",
    "fig-w-seneca": "罗马的斯多葛派哲学家与剧作家，尼禄的导师与密友，后被逼自杀。",
    "fig-w-dante": "意大利诗人，《神曲》的作者，以三界旅程的叙事塑造了现代意大利语。",
    "fig-w-petrarch": "意大利诗人与学者，以《歌集》与对古典文化的整理开启欧洲人文主义。",
    "fig-w-giotto": "意大利画家，以《哀悼基督》等作品把人物与真实情感带入中世纪的画布。",
    "fig-w-thomas-aquinas": "经院哲学的集大成者，以亚里士多德哲学与神学的结合重塑西方思想。",
    "fig-w-roger-bacon": "中世纪的实验科学先驱，以强调经验与实验的方法论批评经院哲学。",
}

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        if e["id"] in SUMMARY:
            e["summary"] = SUMMARY[e["id"]]; changed = True
        for f in ("summary", "biography", "alias", "role", "lifeText"):
            v = e.get(f)
            if isinstance(v, str):
                nv = v
                for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                    nv = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, nv)
                if nv != v:
                    e[f] = nv; changed = True
        for f in ("achievements", "quotes", "tags"):
            if isinstance(e.get(f), list):
                nl = []
                for i in e[f]:
                    s = str(i)
                    for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                        s = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, s)
                    nl.append(s)
                if nl != e[f]:
                    e[f] = nl; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "autofixed")
