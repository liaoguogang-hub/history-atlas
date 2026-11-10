import json, io, sys, glob
sys.stdout.reconfigure(encoding='utf-8')
targets = ['fig-wei-qing','fig-liu-mao','fig-kong-ju-dasha','fig-liang-jin','fig-zhao-gao','fig-liang-wudi','fig-fang-xuanling']
for fn in sorted(glob.glob('data/.tmp/figdata_*.json')):
    d = json.load(io.open(fn, encoding='utf-8'))
    for f in d:
        if f.get('id') in targets:
            print(fn, '|', f['id'], '|', f.get('n'), '| p=', f.get('p'), '| al=', f.get('al'))
