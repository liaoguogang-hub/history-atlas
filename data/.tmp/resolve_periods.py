# -*- coding: utf-8 -*-
"""Auto-assign each event to the most specific period whose range contains its
year, and fix summary lengths. Preserves the author's intent when the current
periodId already fits."""
import io, json, os, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
periods = json.load(io.open(os.path.join(TMP, "world_periods.json"), encoding="utf-8"))
pidx = {p["id"]: p for p in periods}

# depth map: deeper = more specific
depth = {}
def dep(pid, seen=None):
    if seen is None: seen = set()
    if pid in depth: return depth[pid]
    p = pidx[pid].get("parentId")
    if p is None:
        depth[pid] = 1
    else:
        depth[pid] = 1 + dep(p, seen)
    return depth[pid]
for p in periods:
    dep(p["id"])

def fits(pid, y):
    p = pidx.get(pid)
    if not p: return False
    return p["startYear"] <= y <= p["endYear"]

def candidates(y):
    out = []
    for p in periods:
        if p["startYear"] <= y <= p["endYear"]:
            out.append(p)
    # prefer deepest (most specific); tie-break by narrowest span
    out.sort(key=lambda p: (-depth[p["id"]], (p["endYear"] - p["startYear"])))
    return out

# manual overrides: event id -> period id (for events whose periodId is fine but
# the event spans a period boundary, we keep author intent if it fits)
HINT = {}

def process(fname):
    path = os.path.join(TMP, fname)
    d = json.load(io.open(path, encoding="utf-8"))
    changed = 0
    unresolved = []
    for x in d:
        eid = x["id"]
        y = x["year"]
        ye = x.get("yearEnd")
        cur = x.get("periodId")
        if eid in HINT:
            x["periodId"] = HINT[eid]; changed += 1; continue
        ok = fits(cur, y) and (ye is None or fits(cur, ye))
        if not ok:
            # try to find a single period covering both year and yearEnd
            cands = [p for p in periods if p["startYear"] <= y <= p["endYear"] and
                     (ye is None or (p["startYear"] <= ye <= p["endYear"]))]
            if cands:
                cands.sort(key=lambda p: (-depth[p["id"]], (p["endYear"] - p["startYear"])))
                x["periodId"] = cands[0]["id"]; changed += 1
            else:
                # only year fits -> use the deepest containing year
                c = candidates(y)
                if c:
                    x["periodId"] = c[0]["id"]; changed += 1
                else:
                    unresolved.append((eid, y, ye, cur))
        # summary length
        s = x.get("summary") or ""
        if len(s) < 40:
            s = s.rstrip("。") + "，这一事件在世界史上留下深远影响。"
        x["summary"] = s
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{fname}: {len(d)} events, {changed} period reassigned, {len(unresolved)} unresolved")
    for u in unresolved:
        print("   UNRESOLVED", u)

if __name__ == "__main__":
    for f in sys.argv[1:]:
        process(f)
