# -*- coding: utf-8 -*-
"""Patch spec2: remove Latin, fix summary lengths, fix bad reference ids."""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_fig_expand_spec2.json")
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

REPL = [
    ("世界女性学术史上最early的哲学教授形象之一", "世界女性学术史上最早期之一的女性哲学教授形象"),
    ("《利论》（arthashastra）", "《利论》"),
    ("国土、人口、Fortification 与经济四大支柱", "土地、人口、城防与经济四大支柱"),
    ("1769年取得专利，1776年与马特 partnership 建立了波尔顿-瓦特合伙企业",
     "1769年取得专利，1776年与马特合伙建立了波尔顿-瓦特合伙企业"),
    ("以蒸汽机驱动的模型 locomotive", "以蒸汽机驱动的模型机车"),
    ("他晚年 designs 圣彼得大教堂", "他晚年设计圣彼得大教堂"),
    ("出版《花的zygomorphy》式的专门论文", "出版论花的传粉与形态的专门论文"),
    ("生于浙江宁波Ningbo 的一个药师家庭", "生于浙江宁波的一个药师家庭"),
    ("文艺复兴最全面的天才artist", "文艺复兴最全面的天才艺术家"),
    ("为斯福尔扎家族的Ludovico 效力", "为斯福尔扎家族的卢多维科效力"),
    ("其中包括 helicopter、降落伞、坦克与自行车的设想", "其中包括直升机、降落伞、坦克与自行车的设想"),
    ("伴随法国国王 Francis 一世迁居法国", "伴随法国国王弗朗索瓦一世迁居法国"),
    (" painting 是心灵的手艺。", "绘画是心灵的手艺。"),
    ("其设计的“ bombe” 机械装置", "其设计的“战车”式机械装置"),
    ("家族有Chartley 庄园", "家族有查特利庄园"),
    ("1939年9月波兰遭德 invasion 后", "1939年9月波兰遭德国入侵后"),
    ("她与Albert 亲王共同主持", "她与阿尔伯特亲王共同主持"),
    ("“禧年jubilee”（jubilee）", "“禧年庆典”"),
    ("以“Mama Nai”的称呼获得“母亲”的尊称", "以“妈妈奈”的称呼获得“母亲”的尊称"),
    ("成立了“绿带运动”（Green Belt Movement）", "成立了“绿带运动”"),
    ("她与当时正在游行的叙利亚activist 被提名", "她与当时正在游行的叙利亚活动家一同被提名"),
    ("直至2019年因病在 Nairobi 逝世", "直至2019年因病在内罗毕逝世"),
]
for x in d:
    for f in ("summary", "biography", "alias", "role", "lifeText"):
        v = x.get(f)
        if isinstance(v, str):
            for a, b in REPL:
                v = v.replace(a, b)
            x[f] = v
    for f in ("achievements", "quotes", "tags"):
        if isinstance(x.get(f), list):
            x[f] = [str(i).replace("early的哲学", "的哲学") for i in x[f]]
    for f in ("achievements", "quotes", "tags"):
        if isinstance(x.get(f), list):
            new = []
            for i in x[f]:
                s = str(i)
                for a, b in REPL:
                    s = s.replace(a, b)
                new.append(s)
            x[f] = new

# fix bad reference ids
idx["fig-kautilya"]["relatedFigures"] = ["fig-chandragupta", "fig-ashoka", "fig-mansa-musa", "fig-kanishka"]
idx["fig-watt"]["relatedEvents"] = ["ev-discover-price-revolution", "ev-cc-berlin-west-tokyo", "ev-cc-world-expo"]
idx["fig-yuan-longping"]["relatedFigures"] = ["fig-tu-youyou", "fig-shen-kui", "fig-shanfu", "fig-huang-chong"]
idx["fig-victoria"]["relatedFigures"] = ["fig-william-wilberforce", "fig-charles-ellington", "fig-lord-ripon", "fig-jamsetji-tata"]

# summary length fixes
idx["fig-marie-curie"]["summary"] = "放射性元素的发现者，两度获诺贝尔奖，近代物理与化学的奠基性人物。"
idx["fig-yuan-longping"]["summary"] = "杂交水稻的培育者，以显著提高稻谷产量惠及全球数十亿人口而闻名。"
idx["fig-churchill"]["summary"] = "英国首相，以二战中拒绝和谈领导英国御敌，并获诺贝尔文学奖。"
idx["fig-victoria"]["summary"] = "英国女王，其统治期间英国成为世界最大的工业强国与头号全球帝国。"

io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched", len(d))
