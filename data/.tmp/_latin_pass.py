# -*- coding: utf-8 -*-
"""扫描并列出所有 sy_b*.py 中正文类字段的拉丁残留，供人工替换。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LATIN = re.compile(r"[A-Za-z][A-Za-z' ]*")

for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    s = io.open(os.path.join(HERE, fn), encoding='utf-8').read()
    # 提取所有双引号字符串
    hits = []
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', s):
        t = m.group(1)
        if LATIN.search(t):
            hits.append((m.start(), t))
    if hits:
        print('=== %s ===' % fn)
        seen = set()
        for off, t in hits:
            key = t[:40]
            if key in seen:
                continue
            seen.add(key)
            frag = LATIN.search(t)
            print('  %r' % (t[max(0, frag.start() - 30):frag.end() + 30],))
