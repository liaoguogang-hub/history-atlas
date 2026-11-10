# -*- coding: utf-8 -*-
"""Patch exp_specs/b3.json: remove Latin, fix summary lengths, fix bad refs."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs\b3.json"
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

REPL = [
    ("以果断的改革与Aufhebung 式的政策终结了百年分裂", "以果断的改革与破除旧秩序的政策终结了百年分裂"),
    ("受卜部筑紫守的「亲戚Lewis 事件」刺激", "受卜部筑紫守的「亲戚被诛事件」刺激"),
    ("他的统治以打破旧秩序著称： he 大量采用", "他的统治以打破旧秩序著称：他大量采用"),
    ("美国西弗吉尼亚的蓝field", "美国西弗吉尼亚的蓝菲尔德"),
    ("以「 Attention 的重量」与「去根」思想", "以「注意力的重量」与「去根」思想"),
    ("以「 Attention 的重量」这一概念", "以「注意力的重量」这一概念"),
    ("论文研究 Bohr 的积分方程", "论文研究皮卡德的积分方程"),
    ("这使他与沙皇 government 与东正教教会决裂", "这使他与沙皇政府与东正教教会决裂"),
    ("以《别尔庚 memoirs》等自传体作品", "以《童年回忆》等自传体作品"),
    ("此后在西uges温泉疗养期间", "此后在佐治亚的温泉疗养期间"),
    ("他在Battle of Baideng 迎战汉高祖刘邦的四十万大军", "他在白登山迎战汉高祖刘邦的四十万大军"),
    ("1989年柏林墙倒塌时她正在 undergoing 访问", "1989年柏林墙倒塌时她正在国外访问"),
    ("她多次在德国大选后成为欧盟轴心国 leader", "她多次在德国大选后成为欧盟轴心国的领导人"),
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
            new = []
            for i in x[f]:
                s = str(i)
                for a, b in REPL:
                    s = s.replace(a, b)
                new.append(s)
            x[f] = new

# fix bad reference ids
idx["fig-o-kongo"]["relatedFigures"] = ["fig-ito-hirobumi", "fig-yamagata", "fig-murasaki"]
idx["fig-roosevelt"]["relatedFigures"] = ["fig-churchill", "fig-harry-truman", "fig-henry-kissinger", "fig-victoria"]
idx["fig-modu-chanyu"]["relatedFigures"] = ["fig-genghis-khan", "fig-king-wu"]
idx["fig-zhu-de"]["relatedFigures"] = ["fig-dong-biwu", "fig-chen-yun", "fig-zhao-ziyang", "fig-tan-sitong"]
idx["fig-angela-merkel"]["relatedFigures"] = ["fig-eduard-said", "fig-yo-yo-ma", "fig-de-gaulle"]

# summary length fixes
idx["fig-john-nash"]["summary"] = "博弈论的奠基者之一，以纳什均衡解释经济、军事与社会冲突中的稳定策略。"
idx["fig-modu-chanyu"]["summary"] = "匈奴单于，草原帝国的创建者，以骑兵战术与和亲外交迫使汉朝屈服。"

io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched b3")
