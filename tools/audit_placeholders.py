import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    figs = d["figures"]
    placeholder = [f for f in figs if "待补充条目" in (f.get("biography") or "")]
    ascii_ph = [f for f in placeholder
                if re.match(r"^[\x00-\x7F\s]+$", f.get("name") or "")]
    cn_ph = [f for f in placeholder if f not in ascii_ph]
    print(f"--- {sc}: figures={len(figs)}, placeholder={len(placeholder)} ---")
    print(f"  ascii-named placeholders: {len(ascii_ph)}")
    print(f"  chinese-named placeholders: {len(cn_ph)}")
    # ascii placeholder 按 id 前缀聚类，判断是否是「成批重复」的填充
    pref = collections.Counter()
    for f in ascii_ph:
        parts = (f["id"][4:]).split("-")
        pref[parts[0]] += 1
    print("  top prefixes:", dict(list(pref.most_common(12))))
    # 前 20 个 ascii placeholder 的 id
    print("  sample ids:", [f["id"] for f in ascii_ph[:20]])
