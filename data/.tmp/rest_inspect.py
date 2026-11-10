import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(io.open("data/china.json", encoding="utf-8"))
by = {f["id"]: f for f in d["figures"]}
for k in ("fig-wen-zong-2", "fig-wen-zong", "fig-zhang-heng", "fig-peking-man",
          "fig-yuanmou-man", "fig-lantian-man", "fig-li-siyuan-tang"):
    f = by[k]
    print("=" * 70)
    print(k, "|", f["name"], "|", f.get("alias"), "|", f.get("role"))
    print("period:", f.get("periodId"), "| by:", f.get("birthYear"), "-", f.get("deathYear"), "|", f.get("gender"))
    print("biography:", f.get("biography"))
    print("achievements:", f.get("achievements"))
    print("quotes:", f.get("quotes"))
    print("relatedFigures:", f.get("relatedFigures"))
    print("relatedEvents:", f.get("relatedEvents"))
    print("tags:", f.get("tags"))
