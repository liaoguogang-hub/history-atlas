import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def not_after(a, b):
    """a 是否不晚于 b。负数=公元前，数值小=更早，故统一 a <= b。"""
    if a >= 0 and b >= 0:
        return a <= b
    if a < 0 and b < 0:
        return a <= b
    return a < 0 <= b


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    periods = data["periods"]
    by_id = {p["id"]: p for p in periods}

    # 只在「同 scope 的时期」里找更合适的归属，避免跨史域错挂
    scope = data.get("scope")
    prefix = "cn-" if scope == "china" else "w-"
    pool = [p for p in periods if p["id"].startswith(prefix)]

    moved = 0
    for e in data["events"]:
        pid = e.get("periodId")
        p = by_id.get(pid)
        if not p:
            continue
        y = e.get("year")
        ye = e.get("yearEnd")
        ps, pe = p.get("startYear"), p.get("endYear")
        if not all(isinstance(v, int) for v in (y, ps, pe)):
            continue
        if ps <= y <= pe:
            continue  # 已在区间内
        # 找能容纳 [y, ye] 的时期，取区间最贴合者
        cands = []
        for q in pool:
            qs, qe = q.get("startYear"), q.get("endYear")
            if not all(isinstance(v, int) for v in (qs, qe)):
                continue
            if not (qs <= y <= qe):
                continue
            if isinstance(ye, int) and isinstance(qe, int) and ye < qe:
                if not (qs <= ye <= qe):
                    continue
            cands.append(q)
        if not cands:
            continue
        # 优先选区间最窄的（最具体）
        best = min(cands, key=lambda q: q["endYear"] - q["startYear"])
        e["periodId"] = best["id"]
        moved += 1

    # 补展示字段
    for p in periods:
        s, t = p.get("startYear"), p.get("endYear")
        if isinstance(s, int) and not p.get("startDateText"):
            p["startDateText"] = ("公元前%d年" % abs(s)) if s < 0 else ("公元%d年" % s)
        if isinstance(t, int) and not p.get("endDateText"):
            p["endDateText"] = ("公元前%d年" % abs(t)) if t < 0 else ("公元%d年" % t)

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: reassigned {moved} events to better periods, filled date text fields")


if __name__ == "__main__":
    main()
