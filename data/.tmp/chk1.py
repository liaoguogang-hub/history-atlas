import json,re,io,sys
p=r"C:\Users\guoga\Documents\DSH\data\.tmp\world_periods.json"
d=json.load(open(p,encoding="utf-8"))
print("periods:",len(d))
ids=[x["id"] for x in d]
print("unique:",len(set(ids))==len(ids))
bad=[]
for x in d:
    s=json.dumps(x,ensure_ascii=False)
    for m in re.findall(r"[A-Za-z][A-Za-z\.\- ]*[A-Za-z]", s):
        # allow known proper nouns
        if m in ("Bahamas",): continue
        bad.append((x["id"],m))
print("latin tokens:",sorted(set(bad)))
# check year ranges
for x in d:
    assert x["startYear"]<=x["endYear"], x["id"]
print("ranges ok")
