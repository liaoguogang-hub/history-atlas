#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按显式映射表为事件指定时期（覆盖自动分配），并把 yearEnd 截到时期区间内。"""
import json, sys, os

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(D, "world_periods.json"), encoding="utf-8"))
PM = {p["id"]: p for p in P}

# eventId -> periodId
OVERRIDE = {}


def apply(path, mapping):
    raw = json.load(open(path, encoding="utf-8"))
    n = 0
    for it in raw:
        if "role" in it or "ro" in it:
            continue
        eid = it["id"]
        if eid in mapping:
            pid = mapping[eid]
            if pid not in PM:
                print(f"  !! {eid}: 不存在的时期 {pid}")
                continue
            if it.get("p") != pid:
                it["p"] = pid
                n += 1
            p = PM[pid]
            y = it.get("y", it.get("year"))
            ye = it.get("ye", it.get("yearEnd"))
            if not (p["startYear"] <= y <= p["endYear"]):
                print(f"  !! {eid}: year {y} 不在 {pid}[{p['startYear']},{p['endYear']}]")
            if ye is not None and not (p["startYear"] <= ye <= p["endYear"]):
                newye = min(max(ye, p["startYear"]), p["endYear"])
                if newye < y:
                    newye = y
                it["ye"] = newye
                dt = it.get("dt") or it.get("dateText") or ""
                if "－" in dt:
                    head = dt.split("－")[0]
                    pre = "公元前" if y < 0 else "公元"
                    it["dt"] = head + "－" + pre + str(newye) + "年"
    json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{os.path.basename(path)}: 指定 {n} 条")


if __name__ == "__main__":
    m = json.load(open(sys.argv[1], encoding="utf-8"))
    for a in sys.argv[2:]:
        apply(a, m)
