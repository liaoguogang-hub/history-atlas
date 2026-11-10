import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
data = json.load(io.open(path, encoding="utf-8"))

period_ids = {p["id"] for p in data["periods"]}
event_ids = {e["id"] for e in data["events"]}
figure_ids = {f["id"] for f in data["figures"]}

miss_ev = collections.Counter()
miss_fg = collections.Counter()
ev_detail = {}
fg_detail = {}

for p in data["periods"]:
    for eid in (p.get("relatedEvents") or []):
        if eid not in event_ids:
            miss_ev[eid] += 1
            ev_detail.setdefault(eid, p["id"])
    for fid in (p.get("keyFigures") or []):
        if fid not in figure_ids:
            miss_fg[fid] += 1
            fg_detail.setdefault(fid, p["id"])

for e in data["events"]:
    for fid in (e.get("figures") or []):
        if fid not in figure_ids:
            miss_fg[fid] += 1
            fg_detail.setdefault(fid, e["id"])
    for eid in (e.get("relatedEvents") or []):
        if eid not in event_ids:
            miss_ev[eid] += 1
            ev_detail.setdefault(eid, e["id"])

for f in data["figures"]:
    for fid in (f.get("relatedFigures") or []):
        if fid not in figure_ids:
            miss_fg[fid] += 1
            fg_detail.setdefault(fid, f["id"])
    for eid in (f.get("relatedEvents") or []):
        if eid not in event_ids:
            miss_ev[eid] += 1
            ev_detail.setdefault(eid, f["id"])

print(f"=== {path} ===")
print(f"missing events ({len(miss_ev)}):")
for eid, n in miss_ev.most_common():
    print(f"  {eid:32s} x{n}  <- {ev_detail.get(eid)}")
print(f"\nmissing figures ({len(miss_fg)}):")
for fid, n in miss_fg.most_common():
    print(f"  {fid:32s} x{n}  <- {fg_detail.get(fid)}")
