import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
keys = ['li-yao','han-emperor-mingdi','liu-mao','wei-qing','kong-ju','liang-jin','sui-wendi','xiao-yan','fang-xuanling','yao-gun']
for f in p4:
    if any(k in f['id'] for k in keys):
        print(f['id'], '|', f['n'], '|', f.get('al'), '|', f.get('p'), '|', f.get('ro'))
        print('   bio:', (f.get('bio') or '')[:120])
