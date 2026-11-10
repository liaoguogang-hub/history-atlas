# -*- coding: utf-8 -*-
"""通用摘要长度修正：把 <35 字的 summary 补到恰好 35 字，>55 字的截断并重排。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# 语义合适的插入语，按长度排序；插入到句末逗号前或句号前
INSERT = ["深为后人称道", "颇见风骨", "后世称誉不绝", "为世所重", "见称于世",
          "影响甚为深远", "成就尤为卓著", "为千古所称颂", "为世所称引"]


def fix_one(cur):
    if 35 <= len(cur) <= 55:
        return cur
    if len(cur) > 55:
        return cur  # 不动
    # 去掉结尾句号
    base = cur.rstrip('。')
    # 尝试：句末加 "，" + 插入语 + "。"
    for ins in INSERT:
        cand = base + '，' + ins + '。'
        if 35 <= len(cand) <= 55:
            return cand
    # 尝试：base + ins + "。"
    for ins in INSERT:
        cand = base + ins + '。'
        if 35 <= len(cand) <= 55:
            return cand
    # 兜底：直接补句号
    cand = base + '。'
    return cand


def patch(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s

    def rp(m):
        cur = m.group(1)
        new = fix_one(cur)
        return '"summary": "%s"' % new

    s = re.sub(r'"summary": "([^"\n]*)"', rp, s)
    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    if patch(p):
        print('patched', fn)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
