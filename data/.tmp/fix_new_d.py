# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs\d.json"
d = json.load(io.open(P, encoding="utf-8"))
for x in d:
    if x["id"] == "fig-w-jianzhen":
        x["summary"] = "日本高僧，六次东渡入唐，在奈良的唐招提寺建戒坛并传扬戒律与佛法。"
        x["biography"] = x["biography"].replace(
            "以精通医药与-dense 的古典医术知名", "以精通医药与古典医术知名")
        x["biography"] = x["biography"].replace(
            "他还在 temples 之外开设讲席", "他还在寺外开设讲席")
    if x["id"] == "fig-w-augustus-alt":
        x["summary"] = "奥古斯都的本名，罗马帝国的缔造者，以元首制结束百年内战并建立和平。"
io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("ok")
