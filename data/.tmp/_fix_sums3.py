# -*- coding: utf-8 -*-
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 匹配： "summary": <不含引号和换行的文本>",
pat = re.compile(r'("summary": )([^"\n]*)(",)')
for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding='utf-8').read()
    orig = s
    s = pat.sub(lambda m: m.group(1) + '"' + m.group(2) + m.group(3), s)
    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('quote-fix', fn)

for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    try:
        compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
        print('OK', fn)
    except SyntaxError as e:
        print('FAIL', fn, e)
