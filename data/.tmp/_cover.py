# -*- coding: utf-8 -*-
import io, json, os, glob

miss = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = {}
for pid, ids in miss.items():
    for i in ids:
        need[i] = pid

have = {}
for f in sorted(glob.glob('data/.tmp/figdata_*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception as e:
        print('SKIP', f, e); continue
    for x in d:
        have.setdefault(x['id'], []).append(os.path.basename(f))

done = [i for i in need if i in have]
todo = [i for i in need if i not in have]
print('need total:', len(need))
print('done:', len(done))
print('todo:', len(todo))
# check periodId correctness
bad = []
for f in sorted(glob.glob('data/.tmp/figdata_*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    for x in d:
        if x['id'] in need and x.get('p') != need[x['id']]:
            bad.append((x['id'], x.get('p'), need[x['id']]))
print('period mismatch:', bad)

# duplicates
dups = {k: v for k, v in have.items() if len(v) > 1}
print('dup ids across shards:', dups)

# remaining by period
from collections import defaultdict
byp = defaultdict(list)
for i in todo:
    byp[need[i]].append(i)
for p in sorted(byp):
    print(p, len(byp[p]), byp[p])
