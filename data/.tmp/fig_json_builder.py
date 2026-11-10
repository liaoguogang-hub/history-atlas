# -*- coding: utf-8 -*-
"""人物构建器：JSON 片段 -> SCHEMA §4 记录。

数据文件为 JSON 数组，每个元素是一个紧凑对象：
  {"id":..., "name":..., "alias":..., "b":birth, "d":death, "role":...,
   "p":periodId, "g":gender, "s":summary, "bio":biography,
   "ach":[...], "q":[...], "ev":[...], "fg":[...], "t":[...]}
"""
import json
import os
import glob


def build(raw):
    out = []
    for r in raw:
        life = "不详"
        b, d = r.get("b"), r.get("d")
        if b is not None and d is not None:
            bs = "公元前%d年" % abs(b) if b < 0 else "公元%d年" % b
            ds = "公元前%d年" % abs(d) if d < 0 else "公元%d年" % d
            life = bs + "－" + ds
        elif b is not None:
            bs = "公元前%d年" % abs(b) if b < 0 else "公元%d年" % b
            life = bs + "－？"
        elif d is not None:
            ds = "公元前%d年" % abs(d) if d < 0 else "公元%d年" % d
            life = "？－" + ds
        out.append({
            "id": r["id"],
            "name": r["name"],
            "alias": r.get("alias", ""),
            "birthYear": b,
            "deathYear": d,
            "lifeText": life,
            "role": r["role"],
            "periodId": r["p"],
            "gender": r.get("g", "unknown"),
            "summary": r["s"],
            "biography": r["bio"],
            "achievements": list(r.get("ach", [])),
            "quotes": list(r.get("q", [])),
            "relatedEvents": list(r.get("ev", [])),
            "relatedFigures": list(r.get("fg", [])),
            "tags": list(r.get("t", [])),
        })
    return out


def load_all(pattern="figdata_*.json"):
    figs = []
    for f in sorted(glob.glob(pattern)):
        with open(f, "rb") as fh:
            data = json.loads(fh.read().decode("utf-8"))
        for r in data:
            r.setdefault("g", "unknown")
        figs.extend(build(data))
    return figs
