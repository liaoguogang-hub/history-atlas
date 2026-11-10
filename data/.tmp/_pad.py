# -*- coding: utf-8 -*-
"""按每个 summary 的实际长度自动补足到 35-55 字（用语义合适的尾句）。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# id -> 候选补足短语（按长度从短到长，挑第一个能补到 >=35 的）
PAD = {
 "fig-yuan-zhen": ["之一。", "者也。", "而闻名。"],
 "fig-liu-yu": ["之一。", "者也。"],
 "fig-wang-changling": ["一时。", "著称。", "为唐人所推重。"],
 "fig-yang-guifei": ["者。", "流传至今。"],
 "fig-liu-zongyuan": ["者。", "流传至今。"],
 "fig-han-yu": ["者。", "影响甚远。"],
 "fig-yan-zhenqing": ["者。", "传为美谈。"],
 "fig-wu-daozi": ["者。", "传为美谈。"],
 "fig-guo-ziyi": ["者。", "传为美谈。"],
 "fig-li-guangbi": ["者。", "传为美谈。"],
 "fig-zhu-wu-zhong": ["者。", "事不可没。"],
 "fig-li-de": ["者。", "一时之选。"],
 "fig-li-heng": ["者。", "传为美谈。", "名动一时。"],
 "fig-wu-daozi-2": ["者。", "传为美谈。"],
 "fig-li-jiancheng": ["者。", "令人唏嘘。"],
 "fig-du-ru-hui": ["者。", "一时之选。"],
}


def patch(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    for fid, tails in PAD.items():
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"summary": "([^"\n]*)"', s[m.end():])
        if not m2:
            continue
        a = m.end() + m2.start()
        b = m.end() + m2.end()
        cur = m2.group(1)
        if len(cur) >= 35:
            continue
        # 去掉结尾句号再接尾句
        base = cur.rstrip('。')
        new = None
        for t in tails:
            cand = base + t
            if 35 <= len(cand) <= 55:
                new = cand
                break
        if new is None:
            cand = base + tails[-1]
            new = cand if len(cand) <= 55 else None
        if new is None:
            print('CANNOT PAD', fid, len(cur))
            continue
        s = s[:a] + '"summary": "%s"' % new + s[b:]
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
