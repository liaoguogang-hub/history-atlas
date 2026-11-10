import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 修正带空格 / 大写的畸形 id，并同步所有引用。
NAME_FIX = {
    "fig-li- Yuan": ("李元", "将领"),
    "fig-liu Bowen": ("刘昫", "大臣"),
    "fig-li Dazhao": ("李大钊", "思想家"),
}


def slugify(fid):
    """把 id 规范化：小写、连字符分隔、去除空格。"""
    s = re.sub(r"[^0-9a-zA-Z]+", "-", fid).strip("-").lower()
    return s


def main():
    for sc in ["china", "world"]:
        p = f"data/{sc}.json"
        d = json.load(io.open(p, encoding="utf-8"))
        renamed = {}

        # 1) 修正畸形 id
        for item in d.get("figures") or []:
            old = item["id"]
            new = slugify(old)
            if new != old and new not in {f["id"] for f in d["figures"]}:
                renamed[old] = new
                item["id"] = new

        # 2) 修正引用
        for kind in ("periods", "events", "figures"):
            for item in d.get(kind) or []:
                for field in ("keyFigures", "figures", "relatedFigures"):
                    vals = item.get(field)
                    if vals:
                        item[field] = [renamed.get(v, v) for v in vals]

        # 3) 改名
        by_id = {f["id"]: f for f in d.get("figures") or []}
        for old, (nm, role) in NAME_FIX.items():
            # 找改名后的 id
            target = renamed.get(old, old)
            f = by_id.get(target)
            if not f:
                continue
            summary = f"{nm}是这一时期的相关人物，其事迹见于此一时期的史籍记载。"
            f["name"] = nm
            f["role"] = role
            f["summary"] = summary
            if "待补充条目" in (f.get("biography") or ""):
                f["biography"] = f"{nm}，{role}。{summary}"

        io.open(p, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{sc}: renamed {len(renamed)} ids -> {list(renamed.values())}")


if __name__ == "__main__":
    main()
