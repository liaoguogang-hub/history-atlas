# -*- coding: utf-8 -*-
"""修复被 _fix_sums.py 破坏的 summary 引号，并重新做摘要/引文/生平修补。"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 1) 修复引号：形如  "summary": <无引号文本>,  ->  "summary": "<文本>",
pat = re.compile(r'("summary": )([^"\n]+)(,\n)')
for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding='utf-8').read()
    orig = s

    def rp(m):
        return m.group(1) + '"' + m.group(2) + '"' + m.group(3)
    s = pat.sub(rp, s)

    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('quote-fix', fn)

print('--- 校验 JSON 可解析 ---')
for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    try:
        compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
        print('OK', fn)
    except SyntaxError as e:
        print('FAIL', fn, e)
