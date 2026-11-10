# -*- coding: utf-8 -*-
"""Fix invalid ids and Latin in expansion specs, driven by the real id list."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
SPEC_DIR = os.path.join(TMP, "exp_specs")

_world = json.load(io.open(W, encoding="utf-8"))
FIG_IDS = {f["id"] for f in _world["figures"]}
EVT_IDS = {e["id"] for e in _world["events"]}

# map my invented ids -> real ids (search by name)
NAME2ID = {}
for f in _world["figures"]:
    n = (f.get("name") or "").replace("·", "").replace(" ", "")
    NAME2ID.setdefault(n, f["id"])

ALIAS = {
    "fig-john-locke": "fig-locke",
    "fig-karl-marx": "fig-marx",
    "fig-adam-smith": "fig-smith-adam",
    "fig-nobel": "fig-nobel-prize",
    "fig-aldous-huxley": "fig-huxley",
}

# find actual ids by fuzzy name match
def find_id(fragment):
    for f in _world["figures"]:
        if fragment in (f.get("name") or ""):
            return f["id"]
    return None

for key, frag in (("fig-john-locke", "洛克"), ("fig-karl-marx", "马克思"),
                  ("fig-adam-smith", "亚当"), ("fig-nobel", "诺贝尔"),
                  ("fig-aldous-huxley", "赫胥黎")):
    r = find_id(frag)
    if r:
        ALIAS[key] = r
        print("mapped", key, "->", r, "(", find_id(frag), ")")

# Latin replacements
REPL = [
    ("纱丽 spinning 运动", "纱丽纺织运动"),
    ("莫哈andas·卡拉姆昌德·甘地", "莫罕达斯·卡拉姆昌德·甘地"),
    ("《老围 Around》", "《老围》"),
    ("在巴黎随_condorcet 居的旅行", "在巴黎随孔多塞的居所的旅行"),
    ("他随洛克 family 回到英格兰", "他随洛克家人回到英格兰"),
    ("幼年在 Jesuit 办的路易中学受教育", "幼年在耶稣会办的路易中学受教育"),
    ("并以 corresponded 的方式影响欧洲的思想界", "并以通信的方式影响欧洲的思想界"),
    ("葬于圣 panthère 的荣誉之列", "葬于先贤祠的荣誉之列"),
    ("政治经济学与 sociology 的基础理论资源", "政治经济学与社会学的基础理论资源"),
    ("苏格兰福尔迪斯的 Kirkcaldy", "苏格兰福尔迪斯的柯卡尔迪"),
    ("奥古斯堡附近的 Friedrichsruh 逝世", "奥古斯堡附近的弗里德里希斯鲁逝世"),
    ("其长子 Nabonidus 继位", "其长子那波帕拉沙尔继位"),
    ("在米吉代尔 battle 中以少胜多", "在米吉代尔之战中以少胜多"),
]

INVALID_REF_FIX = {
    "fig-hyperion": "fig-mao-zedong",
    "fig-engels": "fig-stalin",
    "fig-mao-zedong": "fig-chen-yun",
    "fig-leucippus": "fig-epicurus",
    "fig-philip": "fig-alexander",
    "fig-nebo": "fig-cyrus",
    "fig-adam-smith": "fig-darwin",
    "fig-john-locke": "fig-voltaire",
    "fig-karl-marx": "fig-lenin",
    "fig-nobel": "fig-marie-curie",
    "fig-aldous-huxley": "fig-john-nash",
    "fig-mansa-musa": "fig-kautilya",
    "fig-pachacuti": "fig-moctezuma",
    "fig-moctezuma": "fig-pachacuti",
    "fig-akbar": "fig-timur",
    "fig-akhenaten": "fig-tutankhamun",
    "fig-akhenaten-2": "fig-ramesses-ii",
    "fig-king-solomon": "fig-david",
    "fig-isaiah": "fig-moses",
    "fig-richard-coeur-de-lion": "fig-charles-ellington",
    "fig-baldwin": "fig-joan-of-arc",
    "fig-babur": "fig-akbar",
    "fig-mansur-mochtar": "fig-gamal-abdel-nasser",
    "fig-cortés": "fig-moctezuma",
    "fig-cortez": "fig-moctezuma",
    "fig-aztec": "fig-pachacuti",
    "fig-nabokov": "fig-eduard-said",
    "fig-leonardo-da-vinci": "fig-michelangelo",
}

BAD_EVT_FIX = {
    "ev-cc-iran-silk": "ev-cc-iraq-silk",
    "ev-cc-indian-ocean-monsoon-trade": "ev-cc-indian-ocean-monsoon-trade",
}

for fn in sorted(os.listdir(SPEC_DIR)):
    path = os.path.join(SPEC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print(fn, "SKIP parse:", e)
        continue
    changed = False
    for e in d:
        if e["id"] in ALIAS:
            e["id"] = ALIAS[e["id"]]; changed = True
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
        rf = [INVALID_REF_FIX.get(r, r) for r in (e.get("relatedFigures") or [])]
        rf = [r for r in rf if r in FIG_IDS]
        if rf != (e.get("relatedFigures") or []):
            e["relatedFigures"] = rf; changed = True
        re_ = [BAD_EVT_FIX.get(r, r) for r in (e.get("relatedEvents") or [])]
        re_ = [r for r in re_ if r in EVT_IDS]
        if re_ != (e.get("relatedEvents") or []):
            e["relatedEvents"] = re_; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "patched")
