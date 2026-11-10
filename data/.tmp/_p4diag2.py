import io, json, collections
main = json.load(io.open('data/china.json', encoding='utf-8'))
ev = set(e['id'] for e in main['events'])
base_figs = set(f['id'] for f in main['figures'])
p4 = json.loads(io.open('data/.tmp/figdata_p4.json', encoding='utf-8').read())
p4ids = set(x['id'] for x in p4)
need = set()
for v in json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8')).values():
    need.update(v)

bad_ev = collections.Counter()
bad_fg = collections.Counter()
for x in p4:
    for e in (x.get('re') or []):
        if e not in ev: bad_ev[e] += 1
    for f in (x.get('rf') or []):
        if f not in base_figs and f not in p4ids and f not in need: bad_fg[f] += 1
print('DANGLING EVENT IDS in p4 (unique):', len(bad_ev))
for k, v in bad_ev.most_common():
    print('  ', k, v)
print()
print('DANGLING FIGURE IDS in p4 (unique):', len(bad_fg))
for k, v in bad_fg.most_common():
    print('  ', k, v)
