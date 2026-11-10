import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/.tmp/figdata_fill2.json', encoding='utf-8'))
for f in d:
    if f.get('id') in ('fig-liu-mao',):
        print(json.dumps(f, ensure_ascii=False, indent=1))
d1 = json.load(io.open('data/.tmp/figdata_fill1.json', encoding='utf-8'))
for f in d1:
    if f.get('id') in ('fig-wei-qing','fig-kong-ju-dasha'):
        print(json.dumps(f, ensure_ascii=False, indent=1)[:900])
