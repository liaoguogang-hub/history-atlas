import io, json, collections
main = json.load(io.open('data/china.json', encoding='utf-8'))
ev = set(e['id'] for e in main['events'])
base_figs = set(f['id'] for f in main['figures'])
p4 = json.loads(io.open('data/.tmp/figdata_p4.json', encoding='utf-8').read())
p4ids = set(x['id'] for x in p4)

# ids referenced by events/periods in main that are NOT defined
refd = collections.defaultdict(set)
for e in main['events']:
    for f in (e.get('figures') or []):
        refd[f].add(e['id'])
for p in main['periods']:
    for f in (p.get('keyFigures') or []):
        refd[f].add('period:' + p['id'])

missing = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = set()
for v in missing.values():
    need.update(v)

print('main figures:', len(base_figs))
print('p4 figures:', len(p4ids))
print('need (missing list):', len(need))
print('need already in main:', len(need & base_figs))
print('need already in p4:', sorted(need & p4ids))
print('need covered by neither:', len(need - base_figs - p4ids))
print()
# dangling refs in main events/periods
dang_ev = [(f, sorted(refd[f])) for f in refd if f not in base_figs and f not in p4ids]
print('main refs dangling & not in need:', len(dang_ev))
print(json.dumps(dang_ev[:20], ensure_ascii=False))
print()
# p4 internal dangling
bad_ev = 0; bad_fg = 0
for x in p4:
    for e in (x.get('re') or []):
        if e not in ev: bad_ev += 1
    for f in (x.get('rf') or []):
        if f not in base_figs and f not in p4ids and f not in need: bad_fg += 1
print('p4 dangling re count:', bad_ev, ' rf count:', bad_fg)
