import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/china.json', encoding='utf-8'))
out = io.open('data/.tmp/_all_ids.txt', 'w', encoding='utf-8')
out.write('=== FIGURES (id | name) ===\n')
for f in d['figures']:
    out.write('%s | %s\n' % (f['id'], f.get('name')))
out.write('\n=== EVENTS (id | name | year) ===\n')
for e in d['events']:
    out.write('%s | %s | %s\n' % (e['id'], e.get('name'), e.get('year')))
out.close()
print('ok')
