import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    c = collections.Counter(e.get("importance") for e in d["events"])
    print(f"--- {sc} importance distribution ---")
    for k in sorted(c, key=lambda x: (x is None, x)):
        print(f"  importance={k}: {c[k]}")
    # 五星事件按年代分布
    hi = [e for e in d["events"] if e.get("importance") == 5]
    print(f"  5-star events: {len(hi)}")
    eras = collections.Counter()
    for e in hi:
        y = e.get("year") or 0
        if y < 0:
            eras["公元前"] += 1
        elif y < 1000:
            eras["公元1-1000"] += 1
        elif y < 1500:
            eras["1000-1500"] += 1
        elif y < 1700:
            eras["1500-1700"] += 1
        elif y < 1912:
            eras["1700-1912"] += 1
        elif y < 1949:
            eras["1912-1949"] += 1
        else:
            eras["1949后"] += 1
    print("   ", dict(eras))
    print("    5-star by century (sample):")
    for e in hi[:20]:
        print(f"      {e.get('year')}  {e.get('name')}")
