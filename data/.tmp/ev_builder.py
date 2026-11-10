# -*- coding: utf-8 -*-
"""事件构建：JSON 紧凑对象 -> SCHEMA §3 记录。"""
import json
import glob


def build(raw):
    out = []
    for r in raw:
        y = r["y"]
        ye = r.get("ye")
        if ye is not None and ye != y:
            date = r.get("dt") or _range_text(y, ye)
        else:
            date = r.get("dt") or _year_text(y)
        out.append({
            "id": r["id"],
            "name": r["n"],
            "year": y,
            "yearEnd": ye,
            "dateText": date,
            "periodId": r["p"],
            "category": r["c"],
            "location": r.get("loc", ""),
            "summary": r["s"],
            "detail": r["d"],
            "importance": r.get("imp", 3),
            "figures": list(r.get("f", [])),
            "tags": list(r.get("t", [])),
        })
    return out


def _year_text(y):
    if y < 0:
        return "公元前%d年" % abs(y)
    return "公元%d年" % y


def _range_text(y1, y2):
    def t(y):
        return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)
    return "%s至%s" % (t(y1), t(y2))


def load_all(pattern="evdata_*.json"):
    evs = []
    for f in sorted(glob.glob(pattern)):
        with open(f, "rb") as fh:
            data = json.loads(fh.read().decode("utf-8"))
        evs.extend(build(data))
    return evs
