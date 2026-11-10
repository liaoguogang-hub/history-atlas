import json, io, sys, glob, re
sys.stdout.reconfigure(encoding='utf-8')

# authoritative ids
amap = json.load(io.open('data/.tmp/figure_period_map.json', encoding='utf-8'))
need = set()
for k, v in json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8')).items():
    need.update(v)

p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
print('p4 count', len(p4))

# strip period prefix heuristics: known period prefixes
PRE = ['qin','han-west','han-east','jin-west','jin-east','liang-jin','nanbei-north','nanbei-south',
       'three-wei','three-shu','three-wu','tang-early','tang-mid','tang-late','song-north','song-south',
       'wudai-north','wudai-south','yuan-early','yuan-late','ming-early','ming-mid','ming-late',
       'qing-early','qing-mid','qing-late','modern-republic','modern-anti-japan','modern-liberation',
       'prc-early','prc-reform','prc-new-era','sixteen-kingdoms','wei-jin-nanbei','spring-autumn',
       'warring-states','zhou-east','zhou-west','xia','shang','prehistory','sui-tang','song-liao-jin',
       'pre-paleolithic','wangmang','wudai','yuan','ming','qing','modern','prc','han','qin','sui','tang','song','liao','jin','xixia','xianbei','fig-']

def strip_pfx(i):
    if i.startswith('fig-'):
        body = i[4:]
    else:
        return None
    for p in PRE:
        if body.startswith(p + '-'):
            return 'fig-' + body[len(p)+1:]
    return None

print('=== p4 mapping ===')
seen = {}
for f in p4:
    nid = strip_pfx(f['id'])
    print(f['id'], '->', nid, 'exists_need=', nid in need if nid else '-', 'exists_map=', nid in amap if nid else '-', 'p=', f.get('p'))
    if nid:
        seen.setdefault(nid, []).append(f['id'])

print('=== dup targets ===')
for k, v in seen.items():
    if len(v) > 1:
        print(k, v)

# events present
evids = set()
for fn in glob.glob('data/.tmp/evdata_*.json'):
    d = json.load(io.open(fn, encoding='utf-8'))
    for e in d:
        evids.add(e['id'])
print('=== event ids ===', len(evids))
WL = ('ev-pre-','ev-xia-','ev-shang-','ev-zhou-','ev-qin-','ev-han-','ev-weijin-','ev-suita-','ev-tang-')
print('legal:', sorted(x for x in evids if x.startswith(WL)))
