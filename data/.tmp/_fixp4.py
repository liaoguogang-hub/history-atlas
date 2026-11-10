import io, json
p = 'data/.tmp/figdata_p4.json'
s = io.open(p, encoding='utf-8', newline='').read()
s = s.replace('"ev-qin-chu"', '"ev-qin-fall"')
s = s.replace('"ev-qin-chensheng-wuguang"', '"ev-qin-chensheng"')
io.open(p, 'w', encoding='utf-8', newline='').write(s)

d = json.loads(io.open(p, encoding='utf-8').read())
main = json.load(io.open('data/china.json', encoding='utf-8'))
ev = set(e['id'] for e in main['events'])
figids = set(f['id'] for f in main['figures']) | set(x['id'] for x in d)
for x in d:
    for e in (x.get('re') or []):
        if e not in ev:
            print('BAD EV', x['id'], e)
    for f in (x.get('rf') or []):
        if f not in figids:
            print('BAD FG', x['id'], f)
print('p4 ok', len(d))
