import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/china.json', encoding='utf-8'))
figs = {f['id']: f for f in d['figures']}
for k in ['fig-wei-qing','fig-liang-wudi','fig-zu-chongzhi','fig-fang-xuanling','fig-hou-jing','fig-shile','fig-liuyuan','fig-tuoba-gui','fig-yuwen-tai','fig-feng-taihou','fig-gao-huan','fig-liuyuan']:
    if k in figs:
        f = figs[k]
        print('EXISTS', k, '|', f.get('n'), '| p=', f.get('p'), '| al=', f.get('al'))
    else:
        print('absent ', k)
# check names of p4 entries for conflicts with existing figure names
p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
names = {f.get('n'): f['id'] for f in d['figures']}
print('--- name conflicts (p4 name already exists in china.json) ---')
for f in p4:
    if f.get('n') in names:
        print(' ', f['id'], f.get('n'), '=> existing', names[f.get('n')])

