# -*- coding: utf-8 -*-
import io, json

miss = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = {}
for pid, ids in miss.items():
    for i in ids:
        need[i] = pid

p1 = json.load(io.open('data/.tmp/figdata_fill1.json', encoding='utf-8'))
p2 = json.load(io.open('data/.tmp/figdata_fill2a.json', encoding='utf-8'))

ids1 = set(x['id'] for x in p1)
# drop from p2 anything already in p1
p2n = [x for x in p2 if x['id'] not in ids1]
# also drop from p2 anything not in the missing list (shouldn't be any)
p2n = [x for x in p2n if x['id'] in need]
# fix period
for x in p2n:
    if x.get('p') != need[x['id']]:
        print('fix period', x['id'], x.get('p'), '->', need[x['id']])
        x['p'] = need[x['id']]

# also fix period in p1
for x in p1:
    if x.get('p') != need.get(x['id']):
        print('fix period', x['id'], x.get('p'), '->', need.get(x['id']))
        x['p'] = need[x['id']]

io.open('data/.tmp/figdata_fill1.json', 'w', encoding='utf-8', newline='').write(json.dumps(p1, ensure_ascii=False, indent=1))
io.open('data/.tmp/figdata_fill2a.json', 'w', encoding='utf-8', newline='').write(json.dumps(p2n, ensure_ascii=False, indent=1))
print('fill1', len(p1), 'fill2a', len(p2n))
