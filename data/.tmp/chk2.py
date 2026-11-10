import re
p=r"C:\Users\guoga\Documents\DSH\data\.tmp\world_periods.json"
s=open(p,encoding="utf-8").read()
lines=s.split("\n")
bad=[]
for i,l in enumerate(lines,1):
    # count quotes; JSON strings have paired quotes. find unescaped inner quotes
    # heuristic: strip valid pairs
    idx=0; inq=False; j=0
    stray=[]
    while j<len(l):
        c=l[j]
        if c=="\\":
            j+=2; continue
        if c=='"':
            if inq:
                # check if this is a closing quote: next non-space char must be , } ] :
                k=j+1
                while k<len(l) and l[k] in " \t": k+=1
                if k<len(l) and l[k] in ",}]:":
                    inq=False
                else:
                    stray.append(j)
            else:
                inq=True
        j+=1
    if stray or inq:
        bad.append((i,len(stray),stray[:6]))
for b in bad: print(b)
print("total bad lines",len(bad))
