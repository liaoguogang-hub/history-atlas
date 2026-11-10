import json,re
p=r"C:\Users\guoga\Documents\DSH\data\.tmp\world_periods.json"
d=json.load(open(p,encoding="utf-8"))
# find latin tokens in Chinese text fields
for x in d:
    for f in ("summary","territory","capital","population","culture","alias"):
        v=x.get(f) or ""
        toks=re.findall(r"[A-Za-z][A-Za-z\.\-']*", v)
        if toks:
            print(x["id"],f,toks)
