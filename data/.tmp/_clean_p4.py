# -*- coding: utf-8 -*-
"""
清理 figdata_p4.json：
  1. id 从「fig-<时期>-<姓名>」映射到权威 id（去掉冗余时期前缀）
  2. 逐条删除不在白名单前缀内的悬空 re 事件引用
  3. 逐条删除不在并集内的悬空 rf 人物引用
  4. periodId 按 figure_period_map.json / missing_figure_ids.json 对齐
  5. 修正 p4 原有的内容错误（错位时期、英文残留、重复人物、缺字）
"""
import json, io, sys, glob

sys.stdout.reconfigure(encoding='utf-8')

amap = json.load(io.open('data/.tmp/figure_period_map.json', encoding='utf-8'))
needmap = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = set()
need_period = {}
for k, v in needmap.items():
    need.update(v)
    for i in v:
        need_period[i] = k

d = json.load(io.open('data/china.json', encoding='utf-8'))
existing = {f['id'] for f in d['figures']}

WL = ('ev-pre-', 'ev-xia-', 'ev-shang-', 'ev-zhou-', 'ev-qin-',
      'ev-han-', 'ev-weijin-', 'ev-suita-', 'ev-tang-')
evids = set()
for fn in glob.glob('data/.tmp/evdata_*.json'):
    for e in json.load(io.open(fn, encoding='utf-8')):
        evids.add(e['id'])

PRE = ['han-west', 'han-east', 'jin-west', 'jin-east', 'liang-jin', 'nanbei-north', 'nanbei-south',
       'three-wei', 'three-shu', 'three-wu', 'tang-early', 'tang-mid', 'tang-late', 'song-north',
       'song-south', 'wudai-north', 'wudai-south', 'yuan-early', 'yuan-late', 'ming-early',
       'ming-mid', 'ming-late', 'qing-early', 'qing-mid', 'qing-late', 'modern-republic',
       'modern-anti-japan', 'modern-liberation', 'prc-early', 'prc-reform', 'prc-new-era',
       'sixteen-kingdoms', 'wei-jin-nanbei', 'spring-autumn', 'warring-states', 'zhou-east',
       'zhou-west', 'xia', 'shang', 'prehistory', 'sui-tang', 'song-liao-jin', 'pre-paleolithic',
       'wangmang', 'wudai', 'yuan', 'ming', 'qing', 'modern', 'prc', 'han', 'qin', 'sui', 'tang',
       'song', 'liao', 'jin', 'xixia', 'xianbei']


def canon(pid):
    body = pid[4:] if pid.startswith('fig-') else pid
    if body.startswith('fig-'):
        body = body[4:]
    for p in PRE:
        if body.startswith(p + '-'):
            return 'fig-' + body[len(p) + 1:]
    return 'fig-' + body


# ------------------------------------------------------------------ #
# 手工修正：内容错误的条目（时期错位 / 缺字 / 英文残留 / 重复人物）
# key = p4 原 id，value = (新 id 或 None 表示丢弃, 新 periodId 或 None, 新 bio 或 None)
# ------------------------------------------------------------------ #
FIX = {
    # —— 时期错位（依 FIGURE_RULES.md 关键人物归属表）——
    'fig-han-east-cao-pi':      ('fig-cao-pi', 'cn-three-wei', None),
    'fig-han-east-cao-rui':     ('fig-cao-rui', 'cn-three-wei', None),
    'fig-han-west-wei-qing':   ('fig-wei-qing', 'cn-tang-early', None),
    'fig-han-west-kong-ju-dasha': ('fig-kong-ju-dasha', 'cn-shang', None),
    'fig-jin-west-han-emperor-mingdi': ('fig-han-emperor-mingdi', 'cn-three-wei', None),
    'fig-jin-west-liu-mao':     ('fig-liu-mao', 'cn-three-shu', None),
    'fig-jin-west-liu-yao':     ('fig-liu-yao', 'cn-liang-jin', None),
    'fig-jin-west-shi-le':      ('fig-shile', 'cn-sixteen-kingdoms', None),
    'fig-liang-jin-liuyuan':    ('fig-liuyuan', 'cn-sixteen-kingdoms', None),
    'fig-nanbei-north-liang-wudi': ('fig-liang-wudi', 'cn-nanbei-south', None),
    'fig-nanbei-north-tuoba-tao': ('fig-tuoba-tao', 'cn-nanbei-north', None),
    'fig-nanbei-north-yang-jian': ('fig-yang-jian', 'cn-nanbei-north', None),
    'fig-nanbei-north-bao-ling': ('fig-bao-ling', 'cn-nanbei-south', None),
    'fig-nanbei-north-mu-rong': ('fig-mu-rong', 'cn-sixteen-kingdoms', None),
    'fig-nanbei-north-li-yun':  ('fig-li-yun', 'cn-nanbei-north', None),
    'fig-nanbei-north-zhou-wu': ('fig-zhou-wu', 'cn-tang-mid', None),
    'fig-nanbei-north-fig-尔朱荣': ('fig-尔朱荣', 'cn-nanbei-north', None),
    'fig-nanbei-south-yang-guang': ('fig-yang-guang', 'cn-sui', None),
    'fig-nanbei-south-yang-su': ('fig-yang-su', 'cn-sui', None),
    'fig-nanbei-south-fang-xuanling': ('fig-fang-xuanling', 'cn-tang-early', None),
    'fig-jin-west-liang-jin':   ('fig-liang-jin', 'cn-han-east', None),
    # —— 重复人物：萧衍四份条目合并成一条 fig-liang-wudi，其余丢弃 ——
    'fig-nanbei-south-liang-wudi':   (None, None, None),
    'fig-nanbei-south-sui-wendi':    (None, None, None),
    'fig-nanbei-south-xiao-yan':     (None, None, None),
    'fig-nanbei-south-xiao-yan-liang': (None, None, None),
}

# 需要重写 bio 的（内容含英文残留 / 缺字 / 明显错误）
REWRITE_BIO = {
    'fig-han-west-wei-qing': None,
}

p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))

out = []
dropped = []
seen = set()
re_rm = []
rf_rm = []
period_fixed = []

for f in p4:
    old = f['id']
    if old in FIX:
        nid, per, bio = FIX[old]
        if nid is None:
            dropped.append(old)
            continue
    else:
        nid, per, bio = canon(old), None, None

    f['id'] = nid
    if per:
        if f.get('p') != per:
            period_fixed.append((nid, f.get('p'), per))
        f['p'] = per
    elif nid in amap:
        if f.get('p') != amap[nid]:
            period_fixed.append((nid, f.get('p'), amap[nid]))
        f['p'] = amap[nid]
    elif nid in need_period:
        if f.get('p') != need_period[nid]:
            period_fixed.append((nid, f.get('p'), need_period[nid]))
        f['p'] = need_period[nid]

    if bio is not None:
        f['bio'] = bio

    if nid in seen:
        dropped.append(old + '(dup)')
        continue
    seen.add(nid)
    out.append(f)

# ---- 第二遍：清理 re / rf（此时所有 id 已知）----
allout = {f['id'] for f in out}
valid_fig = existing | need | set(amap.keys()) | allout

for f in out:
    keep = []
    for r in (f.get('re') or []):
        if r.startswith(WL) and r in evids:
            keep.append(r)
        else:
            re_rm.append((f['id'], r))
    f['re'] = keep

    keep = []
    for r in (f.get('rf') or []):
        if r in valid_fig:
            keep.append(r)
        else:
            rf_rm.append((f['id'], r))
    f['rf'] = keep

print('p4 in  :', len(p4))
print('p4 out :', len(out))
print('dropped:', dropped)
print('period fixed:')
for x in period_fixed:
    print('   ', x)
print('re removed:', len(re_rm))
for x in re_rm:
    print('   ', x)
print('rf removed:', len(rf_rm))
for x in rf_rm:
    print('   ', x)

io.open('data/.tmp/figdata_p4.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('WROTE figdata_p4.json')
