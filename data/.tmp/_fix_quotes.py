# -*- coding: utf-8 -*-
"""通用修复：把以单引号结尾的双引号字符串改成以双引号结尾。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 匹配:  "biography": "<内容>',  ->  "biography": "<内容>",
PAT = re.compile(r'("biography": "[^"\n]*?)' + "'" + r'(,\n\s*"achievements")')

for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding='utf-8').read()
    orig = s
    s = PAT.sub(lambda m: m.group(1) + '"' + m.group(2), s)
    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('fixed', fn)
    try:
        compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
        print('OK', fn)
    except SyntaxError as e:
        print('STILL FAIL', fn, e.lineno, e.msg)
