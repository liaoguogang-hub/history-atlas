import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 把分片里的缩写/异形键统一成 SCHEMA 里的完整键名。
KEY_MAP = {
    "bio": "biography",
    "n": "name",
    "al": "alias",
    "by": "birthYear",
    "dy": "deathYear",
    "lt": "lifeText",
    "ro": "role",
    "p": "periodId",
    "g": "gender",
    "s": "summary",
    "ac": "achievements",
    "q": "quotes",
    "re": "relatedEvents",
    "rf": "relatedFigures",
    "t": "tags",
    "y": "year",
    "ye": "yearEnd",
    "dt": "dateText",
    "c": "category",
    "imp": "importance",
    "loc": "location",
    "d": "detail",
    "f": "figures",
}

for path in sys.argv[1:]:
    raw = io.open(path, encoding="utf-8").read()
    try:
        arr = json.loads(raw)
    except Exception as e:
        print(f"{path}: PARSE FAIL {e}")
        continue

    if isinstance(arr, dict):
        # 已是 {id: {...}} 形式：外层 key 就是 id
        items = []
        for outer_id, body in arr.items():
            if not isinstance(body, dict):
                continue
            it = dict(body)
            it.setdefault("id", outer_id)
            items.append(it)
        keyed = True
    else:
        items = arr
        keyed = False

    changed = 0
    out_items = []
    for it in items:
        if not isinstance(it, dict):
            continue
        new = {}
        for k, v in it.items():
            nk = KEY_MAP.get(k, k)
            if nk != k:
                changed += 1
            new[nk] = v
        out_items.append(new)

    if keyed:
        out = {it["id"]: it for it in out_items if "id" in it}
    else:
        out = out_items

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{path}: {len(out_items)} records, {changed} keys normalized")
