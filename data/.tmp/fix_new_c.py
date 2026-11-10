# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC_DIR = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs"

REPL = [
    ("《Musnad》（按传述者编排的圣训集）与《Sahih》（可信圣训集）",
     "《圣训集》（按传述者编排）与《可信圣训集》"),
    ("《Sunan al-Darimi》", "《达里米圣训集》"),
    ("编纂《Musnad》与《可信圣训集》", "编纂《圣训集》与《可信圣训集》"),
    ("卡帕恰 Kerr 附近", "卡帕恰山一带"),
    ("并获得 tolerated 的支持", "并获得了受宽容的支持"),
    ("并赐予 managing 权", "并赐予治理权"),
]

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        for f in ("summary", "biography", "alias", "role", "lifeText"):
            v = e.get(f)
            if isinstance(v, str):
                nv = v
                for a, b in REPL:
                    nv = nv.replace(a, b)
                if nv != v:
                    e[f] = nv; changed = True
        for f in ("achievements", "quotes", "tags"):
            if isinstance(e.get(f), list):
                nl = []
                for i in e[f]:
                    s = str(i)
                    for a, b in REPL:
                        s = s.replace(a, b)
                    nl.append(s)
                if nl != e[f]:
                    e[f] = nl; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "fixed")
