import json, io, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('data/china.json', encoding='utf-8'))
figs = {f['id'] for f in d['figures']}
evs = {e['id'] for e in d['events']}
print('=== period keyFigures missing ===')
kf = []
for p in d['periods']:
    for f in (p.get('keyFigures') or []):
        if f not in figs:
            kf.append((p['id'], f))
for x in kf: print(' ', x)
print('count', len(kf))
print('=== period relatedEvents missing ===')
re_ = []
for p in d['periods']:
    for e in (p.get('relatedEvents') or []):
        if e not in evs:
            re_.append((p['id'], e))
for x in re_: print(' ', x)
print('count', len(re_))
print('=== event figures missing ===')
ef = []
for e in d['events']:
    for f in (e.get('figures') or []):
        if f not in figs: ef.append((e['id'], f))
for x in ef: print(' ', x)
print('count', len(ef))
print('=== figure relatedEvents/relatedFigures missing ===')
fr = []
for f in d['figures']:
    for x in (f.get('relatedEvents') or []):
        if x not in evs: fr.append((f['id'],'re',x))
    for x in (f.get('relatedFigures') or []):
        if x not in figs: fr.append((f['id'],'rf',x))
for x in fr: print(' ', x)
print('count', len(fr))
