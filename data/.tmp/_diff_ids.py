# -*- coding: utf-8 -*-
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ids = []
for fn in ('sy_b1.py', 'sy_b2.py', 'sy_b3.py'):
    s = io.open(os.path.join(HERE, fn), encoding='utf-8').read()
    found = re.findall(r'"id": "([^"]+)"', s)
    print(fn, len(found))
    ids.extend(found)
sh = json.load(io.open(os.path.join(HERE, 'figdata_expand_songyuan.json'), encoding='utf-8'))
shids = [f['id'] for f in sh]
print('shard n=%d src n=%d' % (len(shids), len(ids)))
print('in shard not in src:', set(shids) - set(ids))
print('in src not in shard:', set(ids) - set(shids))
print('dup in src:', sorted(set(x for x in ids if ids.count(x) > 1)))
