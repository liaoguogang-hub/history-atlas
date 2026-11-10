# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs\a.json"
d = json.load(io.open(SRC, encoding="utf-8"))
idx = {x["id"]: x for x in d}

idx["fig-w-cicero"]["relatedFigures"] = ["fig-julius-caesar", "fig-augustus", "fig-w-seneca", "fig-socrates", "fig-plato"]
idx["fig-w-nero"]["relatedFigures"] = ["fig-w-seneca", "fig-julius-caesar", "fig-augustus", "fig-marcus-aurelius", "fig-constantine"]
idx["fig-w-trajan"]["relatedFigures"] = ["fig-w-hadrian", "fig-augustus", "fig-marcus-aurelius", "fig-darius"]
idx["fig-w-diocletian"]["summary"] = "罗马末期的皇帝，以四帝共治与税制军制的全面改革重建了帝国秩序。"
idx["fig-w-gregory-i"]["summary"] = "罗马教皇，以编纂教令集与整顿教会行政重建了罗马教会的权威。"
idx["fig-w-gregory-i"]["relatedFigures"] = ["fig-constantine", "fig-justinian", "fig-muhammad", "fig-ibn-sina"]
idx["fig-w-giotto"]["relatedEvents"] = ["ev-med-euro-black-death", "ev-ren-brunelleschi-perspective", "ev-ren-humanism-petrarch", "ev-med-euro-gothic-cathedral"]
idx["fig-w-thomas-aquinas"]["biography"] = idx["fig-w-thomas-aquinas"]["biography"].replace(
    "被教会在1323年封为圣人与教义Doctor", "被教会在1323年封为圣人与教义的博士")
idx["fig-w-thomas-aquinas"]["quotes"] = ["信仰寻求理解，理解追求信仰。"]
idx["fig-w-thomas-aquinas"]["relatedFigures"] = ["fig-ibn-sina", "fig-socrates", "fig-plato", "fig-aristotle", "fig-omar-khayyam"]

io.open(SRC, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched a.json")
