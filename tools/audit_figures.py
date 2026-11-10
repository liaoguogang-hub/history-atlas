import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    figs = d["figures"]
    ascii_names = [
        f'{f["id"]} -> {f["name"]}'
        for f in figs
        if re.match(r"^[\x00-\x7F\s]+$", f.get("name") or "")
    ]
    placeholder = [
        f["id"] for f in figs if "待补充条目" in (f.get("biography") or "")
    ]
    roles = collections.Counter(f.get("role") for f in figs)
    print(f"--- {sc}: figures={len(figs)} ---")
    print("  ascii names:", len(ascii_names), ascii_names[:8])
    print("  placeholder:", len(placeholder), placeholder[:6])
    print("  roles:", dict(list(roles.most_common(8))))
