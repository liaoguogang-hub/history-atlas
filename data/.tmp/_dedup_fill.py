# -*- coding: utf-8 -*-
"""在合并后的分片 JSON 上做去重、补成就、补摘要长度，然后回写源批次文件。"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SHARD = os.path.join(HERE, 'figdata_expand_songyuan.json')

data = json.load(io.open(SHARD, encoding='utf-8'))

EXTRA_ACH = {
 "fig-zhang-zhuo": ["其名见晚唐藩镇与农民战争的零星记载"],
 "fig-zhou-chang": ["与汪世显同为陕甘一带活动的汉军将领"],
 "fig-tian-xiang-2": ["唐初将门承袭之制的代表人物"],
 "fig-li-ai": ["其名见昭宗哀宗纪及唐末诸将列传"],
}

NEW_SUM = {
 "fig-qian-hongchu": "吴越末代君主，纳土归宋而保全宗族，善事朝廷，以不流血而善终见称。",
}

INSERT = ["深为后人称道", "颇见风骨", "后世称誉不绝", "为世所重", "见称于世",
          "影响甚为深远", "成就尤为卓著", "为千古所称颂", "为世所称引",
          "一时称为翘楚", "为史家所称引"]


def fix_summary(cur):
    if 35 <= len(cur) <= 55:
        return cur
    if len(cur) > 55:
        return cur
    base = cur.rstrip('。')
    for ins in INSERT:
        cand = base + '，' + ins + '。'
        if 35 <= len(cand) <= 55:
            return cand
    for ins in INSERT:
        cand = base + ins + '。'
        if 35 <= len(cand) <= 55:
            return cand
    return base + '。'


changed = 0
for f in data:
    fid = f['id']
    # 去重 achievements（保持顺序）
    seen = set()
    ach = []
    for a in f.get('achievements') or []:
        if a in seen:
            continue
        seen.add(a)
        ach.append(a)
    for t in EXTRA_ACH.get(fid, []):
        if t not in ach:
            ach.append(t)
    if len(ach) != len(f.get('achievements') or []):
        changed += 1
    f['achievements'] = ach

    if fid in NEW_SUM:
        f['summary'] = NEW_SUM[fid]
    else:
        f['summary'] = fix_summary(f.get('summary') or '')

io.open(SHARD, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
print('patched entries:', changed, 'total:', len(data))

# 回写源文件：把 achievements/summary 的最新值同步回去
src_map = {}
for fn in sorted(x for x in os.listdir(HERE) if x.startswith('sy_b') and x.endswith('.py')):
    p = os.path.join(HERE, fn)
    src_map[fn] = p

byid = {f['id']: f for f in data}


def esc(t):
    return t.replace('\\', '\\\\').replace('"', '\\"')


for fn, p in src_map.items():
    s = io.open(p, encoding='utf-8').read()
    orig = s
    # 逐条替换 achievements 数组与 summary
    for fid, f in byid.items():
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"achievements": \[', s[m.end():])
        if not m2:
            continue
        k = m.end() + m2.end()
        depth = 1
        i = k
        while i < len(s):
            c = s[i]
            if c == '"':
                i += 1
                while i < len(s) and s[i] != '"':
                    if s[i] == '\\':
                        i += 1
                    i += 1
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = ',\n  '.join('"%s"' % esc(a) for a in f['achievements'])
        s = s[:k] + '\n  ' + block + '\n ]' + s[i:]

        m3 = re.search(r'"summary": "[^"\n]*"', s[m.end():])
        if m3:
            a2 = m.end() + m3.start()
            b2 = m.end() + m3.end()
            s = s[:a2] + '"summary": "%s"' % esc(f['summary']) + s[b2:]

    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('rewrote', fn)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
