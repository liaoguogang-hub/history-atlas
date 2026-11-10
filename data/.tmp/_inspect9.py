import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
print(type(d), len(d))
print(json.dumps(d[0], ensure_ascii=False, indent=1))
print('IDS:')
for f in d:
    print(f['id'], '|', f['n'], '|', f.get('p'))
