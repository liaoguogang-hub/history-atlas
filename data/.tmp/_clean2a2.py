# -*- coding: utf-8 -*-
import io, json

p = 'data/.tmp/figdata_fill2a.json'
s = io.open(p, encoding='utf-8').read()

REPS = [
    (u'deprecated', u''),
    (u'northern', u''),
    (u'interrupting', u''),
    (u'battles', u''),
    (u'ERRANT', u''),
    (u'Saying', u''),
    (u'FIGURE', u''),
    (u'subsequently', u''),
    (u'established', u''),
    (u'keshi', u''),
    (u'kindred', u''),
    (u'}-forms', u''),
    (u'hinders', u''),
    (u'Fresh', u''),
    (u'disparity', u''),
    (u'defeat', u''),
    (u'_flagship', u''),
    (u'Luis Luis ', u''),
    (u'oris', u''),
    (u'Masquerade', u''),
    (u'runs', u''),
    (u'.Callback', u''),
    (u"doesn't.", u''),
    (u'steals', u''),
    (u'fled', u''),
    (u' loss', u''),
    (u' park ', u' '),
    (u'Hemidt', u''),
    (u'delay', u''),
    (u'revolution', u''),
    (u'abolish', u''),
    (u'accusation', u''),
    (u'Faraday', u''),
    (u'died', u''),
    (u'Fresh', u''),
    (u'born', u''),
]

for a, b in REPS:
    if a in s and a != b:
        s = s.replace(a, b)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
d = json.loads(io.open(p, encoding='utf-8').read())
print('parsed OK', len(d))
