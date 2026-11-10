import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    ev_no_detail = [e for e in d["events"] if not (e.get("detail") or "").strip()]
    ev_thin = [e for e in d["events"]
               if (e.get("detail") or "").strip()
               and len(e["detail"]) < 180]
    fg_placeholder = [f for f in d["figures"]
                       if "待补充条目" in (f.get("biography") or "")]
    fg_thin = [f for f in d["figures"]
               if f not in fg_placeholder
               and len(f.get("biography") or "") < 120]

    print(f"=== {sc} ===")
    print(f"  events: {len(d['events'])}, no detail: {len(ev_no_detail)}, "
          f"thin(<180): {len(ev_thin)}")
    print(f"  figures: {len(d['figures'])}, placeholder: {len(fg_placeholder)}, "
          f"thin(<120): {len(fg_thin)}")

    if sc == "world":
        print("\n  -- world events by period --")
        c = collections.Counter(e.get("periodId") for e in d["events"])
        pmap = {p["id"]: p.get("name") for p in d["periods"]}
        for pid, n in c.most_common(20):
            print(f"    {n:4d}  {pid:28s} {pmap.get(pid)}")
        print("\n  -- world placeholder figures by period --")
        c2 = collections.Counter(f.get("periodId") for f in fg_placeholder)
        for pid, n in c2.most_common(15):
            print(f"    {n:4d}  {pid:28s} {pmap.get(pid)}")
        print("\n  -- placeholder figure ids --")
        print("   ", " ".join(f["id"] for f in fg_placeholder))
