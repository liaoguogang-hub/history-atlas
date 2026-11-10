# -*- coding: utf-8 -*-
"""修正 achievements 追加位置错误：把误插入到字符串内部的条目挪到数组末尾。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 找出 "xxx['yyy']" 这种误插入，整体还原为 "xxx"，再正确追加
pat = re.compile(r'(,?)\s*"([^"]*)\[\'([^\']*)\'\]"')


def fix(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s

    # 1) 先把 "xxx['yyy']" 还原成 "xxx"，并记录 yyy 待追加
    pending = []

    def rp(m):
        pending.append(m.group(3))
        return '%s"%s"' % (m.group(1), m.group(2))

    s = pat.sub(rp, s)

    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        print('reverted', path, pending)
    return pending


# 逐文件处理，把 pending 条目追加到对应 id 的 achievements 末尾
def add_achievements(path, items):
    """items: list of (id, text)"""
    s = io.open(path, encoding='utf-8').read()
    orig = s
    for fid, text in items:
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"achievements": \[', s[m.end():])
        if not m2:
            continue
        k = m.end() + m2.end()
        depth = 1
        i = k
        while i < len(s) and depth:
            c = s[i]
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
            i += 1
        # i 指向 ] 的下一位；往前找最后一个换行
        j = s.rfind('\n', k, i)
        s = s[:j + 1] + '  "%s"\n' % text + s[j + 1:]
    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    pend = fix(p)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
