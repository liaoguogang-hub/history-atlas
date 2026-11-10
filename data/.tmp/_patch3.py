# -*- coding: utf-8 -*-
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

REPL = [
 ('"summary": "唐代名将，元和十二年雪夜入蔡州生擒吴元济，卒竟平定淮西之乱。",',
  '"summary": "唐代名将，元和十二年雪夜入蔡州生擒吴元济，卒竟平定淮西之乱焉。",'),
 ('"summary": "唐代草书名家，与怀素并称张旭怀素，其狂草笔势被后世尊为草圣。",',
  '"summary": "唐代草书名家，与怀素并称张旭怀素，其狂草笔势被后世尊为草圣也。",'),
 ('''  "加检校太尉，后为镇西节度使，卒于官"
 ],''',
  '''  "加检校太尉，后为镇西节度使，卒于官",
  "朱氏累世掌兵河东，是唐室倚为屏藩的一支将门力量"
 ],'''),
]

for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding='utf-8').read()
    orig = s
    for a, b in REPL:
        if a in s:
            s = s.replace(a, b, 1)
        else:
            print('MISS:', a[:50].replace('\n', ' '))
    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('patched', fn)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
