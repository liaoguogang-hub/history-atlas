"""统计自动生成的空壳事件。

判定标准：摘要命中 auto_fill_dangling 的固定模板，说明该事件从未被真正撰写过，
名字多半是从 id 猜出来的（如 ev-jin-* 被猜成「金朝」，实际挂在两晋下）。
"""
import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

TEMPLATE = re.compile(r"时期的重要事件，与这一阶段的政治格局和社会变动直接相关。$")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    pm = {p["id"]: p for p in d["periods"]}

    fake = [e for e in d["events"] if TEMPLATE.search(e.get("summary") or "")]
    print(f"=== {sc} ===")
    print(f"  事件总数 {len(d['events'])}，模板空壳 {len(fake)}")

    c = collections.Counter(e["periodId"] for e in fake)
    for pid, n in c.most_common(15):
        print(f"    {n:3d}  {pid:24s} {pm.get(pid, {}).get('name')}")

    if sc == "china":
        print("\n  空壳事件清单:")
        for e in sorted(fake, key=lambda x: x.get("periodId") or ""):
            print(f"    {e['id']:38s} {(e.get('name') or ''):24s} {e.get('periodId')}")
