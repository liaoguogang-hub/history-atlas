import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
p4 = json.load(io.open('data/.tmp/figdata_p4.json', encoding='utf-8'))
for f in p4:
    print('###', f['id'], '|', f['n'], '| p=', f.get('p'), '| al=', f.get('al'), '| ro=', f.get('ro'))
    print('  bio:', (f.get('bio') or '')[:160].replace('\n',' '))
