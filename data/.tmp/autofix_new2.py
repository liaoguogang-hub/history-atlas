# -*- coding: utf-8 -*-
"""Fix Latin words in new-figure specs (b, c) and skip already-merged ids."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SRC_DIR = os.path.join(TMP, "new_specs")
W = r"C:\Users\guoga\Documents\DSH\data\world.json"

_world = json.load(io.open(W, encoding="utf-8"))
EXISTING = {f["id"] for f in _world["figures"]}

DICT = {
    "(Media)": "（于两河上游）", "favoured": "的关照", "downtown": "",
    "Elements of Law": "法律要论", "extraordinary": "非凡", "appetition": "趋求",
    "successors": "继任者", "dies": "山谷", "undertaken": "《",
    "itinerant": "云水", "Med ia": "", "Media": "麦地亚",
    "periodId": "", "necessity": "必然",
}
SUMMARY = {}

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    keep, dropped = [], []
    for e in d:
        if e["id"] in EXISTING:
            dropped.append(e["id"])
            continue
        keep.append(e)
    changed = dropped != []
    for e in keep:
        for f in ("summary", "biography", "alias", "role", "lifeText"):
            v = e.get(f)
            if isinstance(v, str):
                nv = v
                for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                    if a:
                        nv = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, nv)
                nv = nv.replace("《 undertaken", "《").replace("、downtown ", "、")
                if nv != v:
                    e[f] = nv; changed = True
        for f in ("achievements", "quotes", "tags"):
            if isinstance(e.get(f), list):
                nl = []
                for i in e[f]:
                    s = str(i)
                    for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                        if a:
                            s = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, s)
                    nl.append(s)
                if nl != e[f]:
                    e[f] = nl; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(keep, ensure_ascii=False, indent=1))
        print(fn, "fixed", "dropped:" + ",".join(dropped) if dropped else "")
