import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

total_bad = 0
for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    bad_ev = [(e["id"], e.get("name")) for e in d["events"]
              if re.search(r"[A-Za-z]", e.get("name") or "")]
    bad_fg = [(f["id"], f.get("name")) for f in d["figures"]
              if re.search(r"[A-Za-z]", f.get("name") or "")]
    bad_per = [(p["id"], p.get("name")) for p in d["periods"]
               if re.search(r"[A-Za-z]", p.get("name") or "")]
    bad_sum = [(e["id"], e.get("summary")) for e in d["events"]
               if re.search(r"[A-Za-z]", e.get("summary") or "")]
    bad_det = [(e["id"], (e.get("detail") or "")[:60]) for e in d["events"]
               if re.search(r"[A-Za-z]", e.get("detail") or "")]

    print(f"--- {sc} ---")
    print(f"  periods={len(d['periods'])} events={len(d['events'])} "
          f"figures={len(d['figures'])}")
    print(f"  latin in period name: {len(bad_per)}")
    for x in bad_per[:5]:
        print("     ", x)
    print(f"  latin in event name : {len(bad_ev)}")
    for x in bad_ev[:5]:
        print("     ", x)
    print(f"  latin in figure name: {len(bad_fg)}")
    for x in bad_fg[:5]:
        print("     ", x)
    print(f"  latin in event summary: {len(bad_sum)}")
    for x in bad_sum[:5]:
        print("     ", x)
    print(f"  latin in event detail : {len(bad_det)}")
    for x in bad_det[:5]:
        print("     ", x)

    total_bad += len(bad_ev) + len(bad_fg) + len(bad_per) + len(bad_sum) + len(bad_det)

print()
print("TOTAL latin-containing fields:", total_bad)
