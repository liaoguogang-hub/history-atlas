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

miss = sorted(k for k in need if k not in figs)
print("total missing:", len(miss))

byper = collections.defaultdict(list)
for fid in miss:
    byper[need[fid]].append(fid)

for pid in sorted(byper):
    print(f"\n{pid} ({len(byper[pid])}):")
    print("  " + ", ".join(sorted(byper[pid])))

io.open("data/.tmp/missing_figure_ids.json", "w", encoding="utf-8").write(
    json.dumps({k: sorted(v) for k, v in byper.items()}, ensure_ascii=False, indent=1)
)
print("\nwrote data/.tmp/missing_figure_ids.json")
