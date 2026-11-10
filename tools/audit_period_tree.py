"""检查时期树的结构问题：时间断层、重叠、子时期越界、命名重复。"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

d = json.load(io.open("data/china.json", encoding="utf-8"))
periods = d["periods"]
by_id = {p["id"]: p for p in periods}
kids = {}
for p in periods:
    kids.setdefault(p.get("parentId"), []).append(p)


def fmt(y):
    return f"前{-y}" if isinstance(y, int) and y < 0 else str(y)


def span(p):
    s, e = p.get("startYear"), p.get("endYear")
    return (s, e) if isinstance(s, int) and isinstance(e, int) else (None, None)


print("=== 1. 子时期区间越出父时期 ===")
for p in periods:
    par = by_id.get(p.get("parentId"))
    if not par:
        continue
    cs, ce = span(p)
    ps, pe = span(par)
    if None in (cs, ce, ps, pe):
        continue
    if cs < ps or ce > pe:
        print(f"  {p['id']:24s} {p.get('name'):8s} [{fmt(cs)}..{fmt(ce)}] "
              f"越出父 {par['id']} [{fmt(ps)}..{fmt(pe)}]")

print("\n=== 2. 顶层时期的时间断层与重叠（按起始年排序）===")
tops = sorted([p for p in periods if not p.get("parentId")],
              key=lambda p: span(p)[0] if span(p)[0] is not None else 0)
prev = None
for p in tops:
    s, e = span(p)
    if prev:
        pps, ppe = span(prev)
        if pps is not None and ppe is not None and s is not None:
            if s > ppe:
                print(f"  断层 {fmt(ppe)} → {fmt(s)}  ({prev.get('name')} → {p.get('name')})")
            elif s < ppe:
                ov = ppe - s
                if ov > 3:
                    print(f"  重叠 {fmt(s)}..{fmt(ppe)} 共{ov}年  ({prev.get('name')} ↔ {p.get('name')})")
    prev = p

print("\n=== 3. 兄弟时期之间的断层 ===")
for par_id, children in kids.items():
    if par_id is None:
        continue
    ch = sorted(children, key=lambda p: span(p)[0] if span(p)[0] is not None else 0)
    print(f"  [{by_id[par_id]['name']}]")
    prev = None
    for c in ch:
        s, e = span(c)
        mark = ""
        if prev:
            ppe = span(prev)[1]
            if isinstance(ppe, int) and isinstance(s, int):
                if s > ppe + 1:
                    mark = f"  ← 断层 {fmt(ppe)}→{fmt(s)}"
                elif s <= ppe:
                    mark = "  ← 重叠"
        print(f"    {c['id']:24s} {c.get('name'):14s} [{fmt(s)}..{fmt(e)}]{mark}")
        prev = c

print("\n=== 4. 同名时期 ===")
name_count = {}
for p in periods:
    name_count.setdefault(p.get("name"), []).append(p["id"])
for n, ids in name_count.items():
    if len(ids) > 1:
        print(f"  {n}: {ids}")
