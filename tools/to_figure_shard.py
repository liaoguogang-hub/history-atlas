import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 把 {id: {...}} 形式的人物补充包转成 merge_shards 认识的数组分片。
# 若输入已是数组则原样规范化字段名。

KEY_MAP = {
    "bio": "biography", "n": "name", "al": "alias",
    "by": "birthYear", "dy": "deathYear", "lt": "lifeText",
    "ro": "role", "p": "periodId", "g": "gender", "s": "summary",
    "ac": "achievements", "q": "quotes", "re": "relatedEvents",
    "rf": "relatedFigures", "t": "tags",
}


def fmt_year(y):
    if y is None:
        return None
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    data = json.load(io.open(src, encoding="utf-8"))

    if isinstance(data, dict):
        items = []
        for outer_id, body in data.items():
            if not isinstance(body, dict):
                continue
            it = dict(body)
            it.setdefault("id", outer_id)
            items.append(it)
    else:
        items = [i for i in data if isinstance(i, dict)]

    out = []
    for it in items:
        rec = {KEY_MAP.get(k, k): v for k, v in it.items()}
        rid = rec.get("id")
        if not rid:
            continue
        by = rec.get("birthYear")
        dy = rec.get("deathYear")
        if not rec.get("lifeText"):
            if by is not None and dy is not None:
                rec["lifeText"] = f"{fmt_year(by)}－{fmt_year(dy)}"
            elif by is not None:
                rec["lifeText"] = f"{fmt_year(by)}－？"
            elif dy is not None:
                rec["lifeText"] = f"？－{fmt_year(dy)}"
            else:
                rec["lifeText"] = "生卒不详"
        rec.setdefault("alias", "")
        rec.setdefault("achievements", [])
        rec.setdefault("quotes", [])
        rec.setdefault("relatedEvents", [])
        rec.setdefault("relatedFigures", [])
        rec.setdefault("tags", [])
        rec.setdefault("gender", "unknown")
        out.append(rec)

    io.open(dst, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{dst}: {len(out)} figures")


if __name__ == "__main__":
    main()
