# -*- coding: utf-8 -*-
"""Check which fig-w-* ids are already merged into world.json."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
w_ids = sorted(f["id"] for f in d["figures"] if f["id"].startswith("fig-w-"))
print("world.json 中 fig-w-* 人物:", len(w_ids))
for i in w_ids:
    print("  ", i)

# what's in my spec dirs not yet merged
FIG_IDS = {f["id"] for f in d["figures"]}
pending = []
for fn in sorted(os.listdir(os.path.join(TMP, "new_specs"))):
    try:
        for e in json.load(io.open(os.path.join(TMP, "new_specs", fn), encoding="utf-8")):
            if e["id"] not in FIG_IDS:
                pending.append((fn, e["id"], e["name"]))
    except Exception:
        pass
print()
print("尚未合并的:", len(pending))
for fn, i, n in pending:
    print("   %-10s %-28s %s" % (fn, i, n))
