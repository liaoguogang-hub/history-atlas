"""规范化 alias 字段。

问题形态：
- alias 与 name 完全相同（「庞涓」/「庞涓」），界面上会出现重复显示
- alias 内部重复（「摩西、摩西」）
- alias 列表里包含 name 本身（「伊尹、挚、阿衡」），应当只保留真别名
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SPLIT = re.compile(r"[、,，/]")


def clean_alias(name, alias):
    name = (name or "").strip()
    alias = (alias or "").strip()
    if not alias:
        return ""
    parts = [p.strip() for p in SPLIT.split(alias) if p.strip()]
    out = []
    for p in parts:
        if p == name:
            continue
        if p in out:
            continue
        out.append(p)
    return "、".join(out)


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        n = 0
        for key in ("periods", "events", "figures"):
            for item in d.get(key) or []:
                if "alias" not in item:
                    continue
                before = item.get("alias") or ""
                after = clean_alias(item.get("name"), before)
                if after != before:
                    item["alias"] = after
                    n += 1
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: cleaned {n} alias fields")


if __name__ == "__main__":
    main()
