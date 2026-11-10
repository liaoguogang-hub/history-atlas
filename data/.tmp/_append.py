import io, json, sys, os

main = 'data/.tmp/figdata_fill2.json'
adds = sys.argv[1:]

base = json.load(io.open(main, encoding='utf-8'))
seen = {x['id'] for x in base}
n = 0
for a in adds:
    arr = json.load(io.open(a, encoding='utf-8'))
    for it in arr:
        if it['id'] in seen:
            print('dup skip', it['id'])
            continue
        seen.add(it['id'])
        base.append(it)
        n += 1

with io.open(main, 'w', encoding='utf-8') as f:
    json.dump(base, f, ensure_ascii=False, indent=1)
print('total', len(base), 'added', n)
