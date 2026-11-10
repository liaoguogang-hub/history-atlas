import json, io, sys, glob
sys.stdout.reconfigure(encoding='utf-8')
needmap = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = set()
for k,v in needmap.items(): need.update(v)
d = json.load(io.open('data/china.json', encoding='utf-8'))
existing = {f['id'] for f in d['figures']}
gap = need - existing
print('gap', len(gap))
PRE = ['han-west','han-east','jin-west','jin-east','liang-jin','nanbei-north','nanbei-south',
       'three-wei','three-shu','three-wu','tang-early','tang-mid','tang-late','song-north',
       'song-south','wudai-north','wudai-south','yuan-early','yuan-late','ming-early',
       'ming-mid','ming-late','qing-early','qing-mid','qing-late','modern-republic',
       'modern-anti-japan','modern-liberation','prc-early','prc-reform','prc-new-era',
       'sixteen-kingdoms','wei-jin-nanbei','spring-autumn','warring-states','zhou-east',
       'zhou-west','xia','shang','prehistory','sui-tang','song-liao-jin','pre-paleolithic',
       'wangmang','wudai','yuan','ming','qing','modern','prc','han','qin','sui','tang',
       'song','liao','jin','xixia','xianbei']
def canon(pid):
    body = pid[4:] if pid.startswith('fig-') else pid
    if body.startswith('fig-'): body = body[4:]
    for p in PRE:
        if body.startswith(p+'-'): return 'fig-'+body[len(p)+1:]
    return 'fig-'+body
p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
p4ids = {canon(f['id']) for f in p4}
print('p4 covers gap ids:', len(gap & p4ids))
print('gap NOT covered by p4:', len(gap - p4ids))
print(sorted(gap - p4ids))
print()
print('p4 ids that are NOT in gap (i.e. already existing or extra):')
for c in sorted(p4ids - gap):
    print('  ', c, 'existing=', c in existing)
