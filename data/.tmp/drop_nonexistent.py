# -*- coding: utf-8 -*-
"""Remove spec entries whose id does not exist in data/world.json
(ids must come from the existing library, never invented).
Then fix remaining summary lengths / achievement counts / Latin."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
SPEC_DIR = os.path.join(TMP, "exp_specs")
_world = json.load(io.open(W, encoding="utf-8"))
FIG_IDS = {f["id"] for f in _world["figures"]}
EVT_IDS = {e["id"] for e in _world["events"]}

REPL = [
    ("被葬于 Targeted 的阿萨福清的陵墓", "被葬于大马士革的阿萨福清的陵墓"),
    ("abolish 强迫的军役制度并以薪金雇佣取代", "废除强迫的军役制度并以薪金雇佣取代"),
    ("其宫廷汇聚了 musician、画家、诗人与学者", "其宫廷汇聚了乐师、画家、诗人与学者"),
    ("他还试图引入西洋的 artillery 与火器技术", "他还试图引入西洋的火炮与火器技术"),
    ("其父以对外征战与扩张而著称， Montezuma 一世在位时", "其父以对外征战与扩张而著称，其父在位时"),
    ("泉州与庆元等港口的海贸繁盛 Marco Polo 等西方旅行者络绎不绝", "泉州与庆元等港口的海贸繁盛，马可·波罗等西方旅行者络绎不绝"),
]

for fn in sorted(os.listdir(SPEC_DIR)):
    path = os.path.join(SPEC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    keep = []
    dropped = []
    for e in d:
        if e["id"] not in FIG_IDS:
            dropped.append(e["id"])
            continue
        for f in ("summary", "biography", "alias", "role", "lifeText"):
            v = e.get(f)
            if isinstance(v, str):
                nv = v
                for a, b in REPL:
                    nv = nv.replace(a, b)
                e[f] = nv
        for f in ("achievements", "quotes", "tags"):
            if isinstance(e.get(f), list):
                e[f] = [str(i) for i in e[f]]
        keep.append(e)
    if dropped:
        print(fn, "dropped:", dropped)
    # filter refs
    for e in keep:
        e["relatedFigures"] = [r for r in (e.get("relatedFigures") or []) if r in FIG_IDS]
        e["relatedEvents"] = [r for r in (e.get("relatedEvents") or []) if r in EVT_IDS]
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(keep, ensure_ascii=False, indent=1))
print("done")
