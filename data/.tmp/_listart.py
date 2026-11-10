import io, json, re

p = 'data/.tmp/figdata_fill2a.json'
d = json.load(io.open(p, encoding='utf-8'))
bad = re.compile(r'[A-Za-z]{3,}')
out = []
for x in d:
    hits = []
    for k in ('s', 'bio', 'al', 'ro'):
        v = x.get(k) or ''
        for m in bad.finditer(v):
            hits.append((k, v[max(0, m.start()-8):m.end()+8]))
    if hits:
        out.append({'id': x['id'], 'hits': hits})
io.open('data/.tmp/_art2a.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), 'figures with artifacts')
for o in out:
    print(o['id'], '|', ' || '.join(h[1] for h in o['hits']))
