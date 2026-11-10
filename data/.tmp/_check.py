import io, json, re, sys, glob

# allowed figure ids union
d = json.load(io.open('data/china.json', encoding='utf-8'))
allowed = {f['id'] for f in d['figures']}
m = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
for v in m.values():
    allowed |= set(v)
# p4 shard ids
for f in glob.glob('data/.tmp/figdata_p*.json'):
    try:
        raw = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    if isinstance(raw, list):
        for it in raw:
            if isinstance(it, dict) and 'id' in it:
                allowed.add(it['id'])
    elif isinstance(raw, dict):
        for k in ('figures',):
            for it in raw.get(k, []) or []:
                if isinstance(it, dict) and 'id' in it:
                    allowed.add(it['id'])

p = sys.argv[1] if len(sys.argv) > 1 else 'data/.tmp/figdata_fill2.json'
arr = json.load(io.open(p, encoding='utf-8'))
print('shard entries:', len(arr))
bad = []
evids = {e['id'] for e in d['events']}
for it in arr:
    for r in (it.get('rf') or []):
        if r not in allowed:
            bad.append((it['id'], 'rf', r))
    for r in (it.get('re') or []):
        if r not in evids:
            bad.append((it['id'], 're', r))
    if it.get('p') not in {x['id'] for x in d['periods']}:
        bad.append((it['id'], 'p', it.get('p')))
    if 'id' not in it or 'n' not in it:
        bad.append((it.get('id'), 'key', 'missing'))
print('BAD refs:', len(bad))
for b in bad:
    print('  ', b)

# id coverage vs missing list
want = set()
for v in m.values():
    want |= set(v)
have = {it['id'] for it in arr}
print('missing ids still absent from shard:', len(want - have))
