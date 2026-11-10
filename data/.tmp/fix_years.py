#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 dateText 中的「公元前／公元」标记修正 year / yearEnd 的正负号，并同步修正 dt 的年份写法。"""
import json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))


def parse_year(txt):
    m = re.search(r"(公元前|公元)\s*(-?\d+)\s*年", txt)
    if not m:
        return None
    n = int(m.group(2))
    return -n if m.group(1) == "公元前" else n


def fmt(year, suffix=""):
    pre = "公元前" if year < 0 else "公元"
    return f"{pre}{abs(year)}年{suffix}"


def fix(path):
    raw = json.load(open(path, encoding="utf-8"))
    n = 0
    for it in raw:
        if "role" in it or "ro" in it:
            continue
        dt = it.get("dt") or it.get("dateText") or ""
        if "－" in dt:
            head, tail = dt.split("－", 1)
            a = parse_year(head)
            b = parse_year(tail)
            if a is None or b is None:
                continue
            if it.get("y") != a:
                it["y"] = a
                n += 1
            if it.get("ye") is not None and it.get("ye") != b:
                it["ye"] = b
                n += 1
            sa = head.split("年", 1)[1] if "年" in head else ""
            sb = tail.split("年", 1)[1] if "年" in tail else ""
            it["dt"] = fmt(a, sa) + "－" + fmt(b, sb)
        else:
            a = parse_year(dt)
            if a is None:
                continue
            if it.get("y") != a:
                it["y"] = a
                n += 1
    json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{os.path.basename(path)}: 修正年份 {n} 处")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        fix(a)
