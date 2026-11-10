"""检查人物/事件的关联完整度。"""
import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    figs = d["figures"]
    evs = d["events"]

    no_ref = [f for f in figs if not (f.get("relatedFigures") or [])
              and not (f.get("relatedEvents") or [])]
    no_ev = [f for f in figs if not (f.get("relatedEvents") or [])]
    no_fg = [f for f in figs if not (f.get("relatedFigures") or [])]
    ev_no_fig = [e for e in evs if not (e.get("figures") or [])]

    print(f"=== {sc} ===")
    print(f"  人物 {len(figs)}：两者皆空 {len(no_ref)}，无相关事件 {len(no_ev)}，"
          f"无相关人物 {len(no_fg)}")
    print(f"  事件 {len(evs)}：无涉及人物 {len(ev_no_fig)}")

    # 关联数量的分布
    c = collections.Counter()
    for f in figs:
        n = len(f.get("relatedFigures") or []) + len(f.get("relatedEvents") or [])
        c["0" if n == 0 else ("1" if n == 1 else ("2-4" if n <= 4 else "5+"))] += 1
    print(f"  关联总数分布: {dict(c)}")

    # 被引用次数（谁最孤立）
    inbound = collections.Counter()
    for f in figs:
        for r in f.get("relatedFigures") or []:
            inbound[r] += 1
    for e in evs:
        for r in e.get("figures") or []:
            inbound[r] += 1
    for p in d["periods"]:
        for r in p.get("keyFigures") or []:
            inbound[r] += 1

    zero_in = [f for f in figs if inbound.get(f["id"], 0) == 0]
    print(f"  从未被任何条目引用: {len(zero_in)}")

    if sc == "china":
        print("\n  示例：孙权")
        for f in figs:
            if f.get("name") == "孙权":
                print(f"    {f['id']} 相关事件={f.get('relatedEvents')}")
                print(f"      相关人物={f.get('relatedFigures')}")
                print(f"      传记 {len(f.get('biography') or '')} 字")
        print("\n  示例：曹操")
        for f in figs:
            if f.get("name") == "曹操":
                print(f"    {f['id']} 相关事件={len(f.get('relatedEvents') or [])} "
                      f"相关人物={len(f.get('relatedFigures') or [])} "
                      f"传记 {len(f.get('biography') or '')} 字")
