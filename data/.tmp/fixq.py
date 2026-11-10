import json
p=r"C:\Users\guoga\Documents\DSH\data\.tmp\world_periods.json"
lines=open(p,encoding="utf-8").read().split("\n")
out=[]
for l in lines:
    res=[]
    inq=False
    j=0
    while j<len(l):
        c=l[j]
        if c=='"':
            if inq:
                k=j+1
                while k<len(l) and l[k] in " \t": k+=1
                if k<len(l) and l[k] in ",}]:":
                    inq=False
                    res.append('"')
                else:
                    # inner quote -> full-width
                    res.append("\u201c" if res.count("\u201c")==res.count("\u201d") else "\u201d")
            else:
                inq=True
                res.append('"')
            j+=1
            continue
        res.append(c); j+=1
    out.append("".join(res))
s="\n".join(out)
open(p,"w",encoding="utf-8",newline="\n").write(s)
d=json.load(open(p,encoding="utf-8"))
print("parsed OK, periods:",len(d))
