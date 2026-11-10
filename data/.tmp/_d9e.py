import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
amap = json.load(io.open('data/.tmp/figure_period_map.json', encoding='utf-8'))
needmap = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = set()
for k,v in needmap.items(): need.update(v)
d = json.load(io.open('data/china.json', encoding='utf-8'))
existing = {f['id'] for f in d['figures']}
print('existing figs in china.json:', len(existing))
# p4 canonical ids not in need and not in existing -> 需要判断保留
p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
PRE = ['han-west','han-east','jin-west','jin-east','liang-jin','nanbei-north','nanbei-south',
       'three-wei','three-shu','three-wu','tang-early','tang-mid','tang-late','song-north','song-south',
       'wudai-north','wudai-south','yuan-early','yuan-late','ming-early','ming-mid','ming-late',
       'qing-early','qing-mid','qing-late','modern-republic','modern-anti-japan','modern-liberation',
       'prc-early','prc-reform','prc-new-era','sixteen-kingdoms','wei-jin-nanbei','spring-autumn',
       'warring-states','zhou-east','zhou-west','xia','shang','prehistory','sui-tang','song-liao-jin',
       'pre-paleolithic','wangmang','wudai','yuan','ming','qing','modern','prc','han','qin','sui','tang',
       'song','liao','jin','xixia','xianbei']
def canon(pid):
    body = pid[4:] if pid.startswith('fig-') else pid
    if body.startswith('fig-'): body = body[4:]
    for p in PRE:
        if body.startswith(p+'-'): return 'fig-'+body[len(p)+1:]
    return pid
out=[]
for f in p4:
    c = canon(f['id'])
    tag = []
    if c not in need: tag.append('NOT_IN_NEED')
    if c not in existing: tag.append('NOT_EXISTING')
    if c not in amap: tag.append('NOT_IN_MAP')
    out.append((f['id'], c, f['n'], f.get('p'), ','.join(tag)))
for o in out:
    if o[4]: print(o)
print('--- counts ---')
print('total p4', len(out))
print('in need:', sum(1 for o in out if 'NOT_IN_NEED' not in o[4]))
