# -*- coding: utf-8 -*-
"""把 sy_b*.py 合并为 figdata_expand_songyuan.json。"""
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

mods = sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py'))
out = []
for m in mods:
    p = os.path.join(HERE, m)
    spec = importlib.util.spec_from_file_location(m[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out.extend(mod.R)
    print('%s -> %d' % (m, len(mod.R)))

# 字段顺序规范化
ORDER = ["id", "name", "alias", "role", "birthYear", "deathYear", "gender",
         "periodId", "summary", "biography", "achievements", "quotes",
         "relatedFigures", "relatedEvents", "tags"]
norm = []
for f in out:
    g = {}
    for k in ORDER:
        if k in f:
            g[k] = f[k]
    for k in f:
        if k not in g:
            g[k] = f[k]
    norm.append(g)

dest = os.path.join(ROOT, 'data', '.tmp', 'figdata_expand_songyuan.json')
io.open(dest, 'w', encoding='utf-8').write(
    json.dumps(norm, ensure_ascii=False, indent=1))
print('WROTE %s  n=%d' % (dest, len(norm)))
