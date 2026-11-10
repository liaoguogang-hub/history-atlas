"""修复被 slugify 压坏的 id。

早期 fix_malformed_ids.py 用 `[^0-9a-zA-Z]+ -> -` 规范化 id，
把含中文的 id（如 `fig-尔朱荣`）压成了 `fig`、`fig-nanbei-north-fig`
这类无意义的值。这里按名字重建正确的 id。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


def slug_from(name):
    return re.sub(r"[^0-9a-zA-Z]+", "-", name).strip("-").lower()


# 已知被压坏的 id → 依据 name 重建
BROKEN = {"fig", "fig-fig"}


def good_id(fid):
    """id 是否有效：fig- 后必须有内容，且不能只剩连字符。"""
    if not fid.startswith("fig-"):
        return False
    body = fid[4:]
    return bool(body.strip("-"))


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        figs = d.get("figures") or []
        existing = {f["id"] for f in figs}
        renames = {}

        for f in figs:
            fid = f["id"]
            # 不规范：不以 fig- 开头，或 fig- 后无内容
            if not fid.startswith("fig-"):
                need = True
                body = fid
            else:
                body = fid[4:]
                need = (not body.strip("-")) or body.endswith("-fig") or body.endswith("-")
            if not need:
                continue
            # 用名字生成 id；中文名无法 slug 时退化为拼音式编号
            base = slug_from(f.get("name") or "")
            if not base:
                prefix = body.rstrip("-fig").strip("-")
                base = (prefix + "-character") if prefix else "character"
            new = "fig-" + base
            if new in existing and new != fid:
                continue
            renames[fid] = new
            existing.discard(fid)
            existing.add(new)

        if not renames:
            print(f"{path}: no broken ids")
            continue

        # 改 id 并同步全部引用
        for f in figs:
            if f["id"] in renames:
                f["id"] = renames[f["id"]]
        for kind in ("periods", "events", "figures"):
            for item in d.get(kind) or []:
                for field in ("keyFigures", "figures", "relatedFigures"):
                    vals = item.get(field)
                    if vals:
                        item[field] = [renames.get(v, v) for v in vals]

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: rebuilt {len(renames)} ids -> {list(renames.items())}")


if __name__ == "__main__":
    main()
