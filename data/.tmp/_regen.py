# -*- coding: utf-8 -*-
"""以 JSON 分片为唯一真源：修复条目并重新生成 sy_b*.py 源文件。"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SHARD = os.path.join(HERE, 'figdata_expand_songyuan.json')

data = json.load(io.open(SHARD, encoding='utf-8'))

EXTRA_ACH = {
 "fig-zhang-zhuo": ["其名见晚唐藩镇与农民战争的零星记载", "为晚唐藩镇武将群体留一名录"],
 "fig-zhou-chang": ["与汪世显同为陕甘一带活动的汉军将领", "汉地武力成为蒙古经略中原的重要支柱"],
 "fig-tian-xiang-2": ["唐初将门承袭之制的代表人物", "其家世以边功累世为将"],
 "fig-li-ai": ["其名见昭宗哀宗纪及唐末诸将列传", "为晚唐藩镇中层将领的一个例证"],
 "fig-shang-rang": ["与尚君长昆仲，皆以勇力称于河南", "其号召之力使数万亡命之徒聚于麾下"],
}

NEW_SUM = {
 "fig-qian-hongchu": "吴越末代君主，纳土归宋而保全宗族，善事朝廷，以不流血而善终见称于世。",
 "fig-shang-rang": "唐末黄巢起义的重要将领，官至太尉中书令，起义失败后投降被杀。",
 "fig-zhang-zhuo": "唐末地方将领，事迹见于晚唐藩镇与农民战争的记载，其名留于史籍。",
 "fig-zhou-chang": "蒙古汗国时期的汉军将领，与汪世显共同经营关中陕甘，卒于南宋作战军中。",
 "fig-tian-xiang-2": "唐初将领，历任边疆要职，参与对吐蕃的多次作战，以边功著称。",
 "fig-li-ai": "唐末将领，事迹见于朱温集团扩张与唐末政局更替的记载。",
}

for f in data:
    fid = f['id']
    seen = set()
    ach = []
    for a in f.get('achievements') or []:
        if a not in seen:
            seen.add(a)
            ach.append(a)
    for t in EXTRA_ACH.get(fid, []):
        if t not in ach:
            ach.append(t)
    f['achievements'] = ach
    if fid in NEW_SUM:
        f['summary'] = NEW_SUM[fid]

io.open(SHARD, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))

# 重新生成源文件（每 20 条一个模块）
ORDER = ["id", "name", "alias", "role", "birthYear", "deathYear", "gender",
         "periodId", "summary", "biography", "achievements", "quotes",
         "relatedFigures", "relatedEvents", "tags"]

for idx in range(0, len(data), 20):
    chunk = data[idx:idx + 20]
    fn = 'sy_b%d.py' % (idx // 20 + 1)
    p = os.path.join(HERE, fn)
    lines = ['# -*- coding: utf-8 -*-',
             '"""批次 %d：唐宋金元人物（自动生成）。"""' % (idx // 20 + 1),
             '', 'R = [']
    for f in chunk:
        lines.append('{')
        for k in ORDER:
            if k not in f:
                continue
            v = f[k]
            if isinstance(v, str):
                lines.append(' %s: %s,' % (json.dumps(k), json.dumps(v, ensure_ascii=False)))
            elif isinstance(v, list):
                if not v:
                    lines.append(' %s: [],' % json.dumps(k))
                else:
                    lines.append(' %s: [' % json.dumps(k))
                    for it in v:
                        lines.append('  %s,' % json.dumps(it, ensure_ascii=False))
                    lines.append(' ],')
            else:
                if v is None:
                    lines.append(' %s: None,' % json.dumps(k))
                else:
                    lines.append(' %s: %s,' % (json.dumps(k), json.dumps(v)))
        lines.append('},')
    lines.append(']')
    io.open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('regen', fn, len(chunk))

# 删除旧的 sy_b*.py（已被覆盖）
print('done')
