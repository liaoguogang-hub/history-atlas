import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
needmap = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
for k in ['cn-nanbei-north','cn-nanbei-south','cn-jin-west','cn-liang-jin']:
    print(k, '->', needmap.get(k))
