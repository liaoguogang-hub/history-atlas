import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

for sc in ["china", "world"]:
    d = json.load(io.open(f"data/{sc}.json", encoding="utf-8"))
    ph = [f for f in d["figures"] if "待补充条目" in (f.get("biography") or "")]
    print(f"--- {sc}: figures={len(d['figures'])}, placeholders={len(ph)} ---")
    # 仍然含拉丁字母的名字（说明音译没覆盖）
    latin = [f["name"] for f in d["figures"]
             if re.search(r"[A-Za-z]", f.get("name") or "")]
    print(f"  names containing latin letters: {len(latin)}")
    for n in latin[:25]:
        print("    ", n)
    # 抽查若干占位翻译
    print("  sample placeholders:")
    for f in ph[:12]:
        print(f"    {f['id']:32s} -> {f['name']}")
