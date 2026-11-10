import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/china.json', encoding='utf-8'))
pm = {p['id']: p.get('name') for p in d['periods']}
T = ('唐','唐前期','唐中期','唐后期','隋','隋唐','五代','五代十国','十国','北宋','南宋','宋辽金','辽','金','西夏','夏','蒙古','蒙古帝国','元','元前期','元后期')
tg = [f for f in d['figures'] if (len(f.get('biography') or '') < 260 or not f.get('achievements')) and pm.get(f.get('periodId')) in T]
out = io.open('data/.tmp/_scope_dump.txt', 'w', encoding='utf-8')
out.write('count %d\n' % len(tg))
for f in tg:
    out.write('=== %s | %s\n' % (f['id'], f.get('name')))
    out.write('  alias: %s | role: %s | %s-%s | %s | periodId: %s (%s)\n' % (
        f.get('alias'), f.get('role'), f.get('birthYear'), f.get('deathYear'),
        f.get('gender'), f.get('periodId'), pm.get(f.get('periodId'))))
    out.write('  lifeText: %s\n' % (f.get('lifeText') or '')[:200])
    out.write('  summary: %s\n' % f.get('summary'))
    out.write('  bio: %s\n' % (f.get('biography') or ''))
    out.write('  ach: %s\n' % json.dumps(f.get('achievements'), ensure_ascii=False))
    out.write('  quotes: %s\n' % json.dumps(f.get('quotes'), ensure_ascii=False))
    out.write('  relF: %s\n' % json.dumps(f.get('relatedFigures'), ensure_ascii=False))
    out.write('  relE: %s\n' % json.dumps(f.get('relatedEvents'), ensure_ascii=False))
    out.write('  tags: %s\n' % json.dumps(f.get('tags'), ensure_ascii=False))
out.close()
print('written', len(tg))
