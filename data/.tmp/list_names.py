# -*- coding: utf-8 -*-
"""Print exact names of figures and events for prose matching."""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
KW = ["穆罕默德", "阿育王", "释迦牟尼", "旃陀罗", "甘地", "尼赫鲁", "屋大维", "奥古斯都",
      "恺撒", "凯撒", "伯里克利", "苏格拉底", "柏拉图", "亚里士多德", "亚历山大",
      "汉尼拔", "尼禄", "图拉真", "哈德良", "戴克里先", "君士坦丁", "西塞罗", "塞内加",
      "但丁", "薄伽丘", "彼特拉克", "乔托", "阿奎那", "培根", "巴格达", "伊本",
      "玄奘", "鉴真", "郑和", "利玛窦", "汤若望", "牛顿", "莱布尼茨", "笛卡尔", "霍布斯",
      "洛克", "伏尔泰", "孟德斯鸠", "卢梭", "狄德罗", "康德", "哥伦布", "麦哲伦",
      "达·伽马", "莎士比亚", "达·芬奇", "米开朗基罗", "歌德", "托马斯"]
print("=== FIGURES (name | id | period) ===")
for f in d["figures"]:
    nm = f.get("name") or ""
    if any(k in nm for k in KW):
        print("  %-16s %-32s %s" % (nm, f["id"], f.get("periodId")))
print()
print("=== EVENTS (name | id | period) ===")
for e in d["events"]:
    nm = e.get("name") or ""
    if any(k in nm for k in KW):
        print("  %-30s %-36s %s" % (nm[:30], e["id"], e.get("periodId")))
