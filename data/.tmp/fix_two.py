import json
p = 'data/.tmp/world_events_b1.json'
d = json.load(open(p, encoding='utf-8'))
n = 0
for it in d:
    if it['id'] == 'ev-rome-latin-church-latin-greece':
        it['p'] = 'w-post-roman-europe'; it['y'] = 476; it['ye'] = 800
        it['dt'] = '公元476年－公元800年'; n += 1
    if it['id'] == 'ev-rome-egypt-ibis':
        it['p'] = 'w-ancient-near-east'; it['y'] = -800; it['ye'] = -800
        it['dt'] = '公元前800年'; n += 1
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', n)
