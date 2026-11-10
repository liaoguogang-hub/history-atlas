import json, io, sys, collections

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
figs = {f["id"] for f in d["figures"]}

need = {}
for e in d["events"]:
    for fid in (e.get("figures") or []):
        need.setdefault(fid, e["periodId"])
for p in d["periods"]:
    for fid in (p.get("keyFigures") or []):
        need.setdefault(fid, p["id"])

missing = sorted(k for k in need if k not in figs)

# load all figure shards, index by id
shards = {}
import glob
for path in sorted(glob.glob("data/.tmp/figdata_*.json")):
    try:
        arr = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print(f"SKIP {path}: {e}", file=sys.stderr)
        continue
    for it in arr:
        shards.setdefault(it["id"], []).append((path, it))

print("shard figure ids:", len(shards))

# For each missing id, find a shard entry whose "name" looks plausible.
# Heuristic: match by id suffix tokens appearing in the shard's alias/name.
def tokens(fid):
    return [t for t in fid.replace("fig-", "").split("-") if len(t) >= 2]

print("\n--- missing ids with candidates in shards ---")
for fid in missing:
    tk = tokens(fid)
    cands = []
    for sid, entries in shards.items():
        if sid == fid:
            cands.append((sid, entries[0][1], "EXACT"))
            continue
        for path, it in entries:
            nm = (it.get("name") or it.get("n") or "")
            al = (it.get("alias") or it.get("al") or "")
            blob = nm + " " + al
            if all(t in blob.lower() for t in tk[:2]) and len(tk) >= 2:
                cands.append((sid, it, "token"))
                break
    if cands:
        print(f"{fid}:")
        for sid, it, kind in cands[:4]:
            print(f"    -> {sid}  [{kind}]  name={it.get('name') or it.get('n')!r}")
    else:
        print(f"{fid}: NO CANDIDATE")
