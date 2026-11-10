import io, json, sys, re

SRC = "data/.tmp/gen_china_periods.py"
DST = "data/.tmp/china_periods_reference.json"

s = io.open(SRC, encoding="utf-8").read()

# The corrupting script replaced ASCII double quotes with U+201C / U+201D.
# Recover by mapping smart quotes back to ASCII quotes, then re-quote
# any Chinese-text internal quotes as corner brackets.
s = s.replace("\u201c", '"').replace("\u201d", '"')

# Extract add(...) call arguments using a small tokenizer.
calls = []
i = 0
n = len(s)
while True:
    j = s.find("add(", i)
    if j < 0:
        break
    # find matching close paren
    k = j + 3
    depth = 0
    args = []
    cur = []
    in_str = False
    while k < n:
        ch = s[k]
        if in_str:
            if ch == '"':
                in_str = False
                args.append("".join(cur))
                cur = []
            elif ch == '\\' and k + 1 < n:
                cur.append(s[k+1]); k += 2; continue
            else:
                cur.append(ch)
        else:
            if ch == '"':
                in_str = True
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            elif ch == ',' and depth == 0:
                args.append("".join(cur)); cur = []
            elif ch == '\n':
                cur.append(' ')
            else:
                cur.append(ch)
        k += 1
    calls.append(args)
    i = k + 1

FIELDS = ["id", "name", "alias", "parent", "sy", "ey", "color",
          "summary", "terr", "cap", "pop", "cult", "tags"]

out = []
for args in calls:
    if len(args) != len(FIELDS):
        continue
    d = dict(zip(FIELDS, args))
    pid = d["id"].strip()
    if not pid.startswith("cn-"):
        continue
    parent = d["parent"].strip()
    if parent == "None":
        parent = None
    sy = int(d["sy"].strip())
    ey = int(d["ey"].strip())
    tags = json.loads(d["tags"].strip())
    out.append({
        "id": pid,
        "name": d["name"].strip(),
        "alias": d["alias"].strip(),
        "parentId": parent,
        "startYear": sy,
        "endYear": ey,
        "startDateText": ("公元前%d年" % -sy) if sy < 0 else ("公元%d年" % sy),
        "endDateText": ("公元前%d年" % -ey) if ey < 0 else ("公元%d年" % ey),
        "colorKey": d["color"].strip(),
        "summary": d["summary"].strip(),
        "territory": d["terr"].strip(),
        "capital": d["cap"].strip(),
        "population": d["pop"].strip(),
        "culture": d["cult"].strip(),
        "keyFigures": [],
        "relatedEvents": [],
        "tags": tags,
    })

json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("periods recovered:", len(out))
print("top-level:", len([p for p in out if not p["parentId"]]))
ids = [p["id"] for p in out]
print("dup ids:", [x for x in set(ids) if ids.count(x) > 1])
