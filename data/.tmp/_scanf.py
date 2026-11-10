# -*- coding: utf-8 -*-
import io, json, re, sys

path = sys.argv[1]
d = json.load(io.open(path, encoding='utf-8'))
bad = re.compile(r'[A-Za-z]{2,}')
buf = []
for x in d:
    for k in ('s', 'bio', 'al', 'ro'):
        v = x.get(k) or ''
        for m in bad.finditer(v):
            buf.append(x['id'] + ' [' + k + '] ' + repr(v[max(0, m.start()-14):m.end()+14]))
# also check for suspicious empty/short fields
for x in d:
    for k in ('s', 'bio'):
        if len(x.get(k) or '') < 60:
            buf.append(x['id'] + ' SHORT ' + k + ' len=' + str(len(x.get(k) or '')))
io.open('data/.tmp/_art.txt', 'w', encoding='utf-8').write('\n'.join(buf))
print(len(buf), 'issues')
