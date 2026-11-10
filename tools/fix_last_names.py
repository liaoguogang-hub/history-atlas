import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FIX = {
    "fig-li-yuan": ("李元", "将领"),
    "fig-shen-kuo": ("沈括", "科学家"),
    "fig-liu-bowen": ("刘昫", "大臣"),
    "fig-li-dazhao": ("李大钊", "思想家"),
    "fig-li-yuan-2": ("李元", "将领"),
    "fig-li-yuan-3": ("李元", "将领"),
}

for sc in ["china", "world"]:
    p = f"data/{sc}.json"
    d = json.load(io.open(p, encoding="utf-8"))
    n = 0
    for f in d["figures"]:
        name = f.get("name") or ""
        if re.search(r"[A-Za-z]", name):
            if f["id"] in FIX:
                nm, role = FIX[f["id"]]
                summary = f"{nm}是这一时期的相关人物，其事迹见于此一时期的史籍记载。"
                f["name"] = nm
                f["role"] = role
                f["summary"] = summary
                if "待补充条目" in (f.get("biography") or ""):
                    f["biography"] = f"{nm}，{role}。{summary}"
                n += 1
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{sc}: fixed {n}")
