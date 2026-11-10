import io, json, re, sys

path = sys.argv[1]
a = json.load(io.open(path, encoding='utf-8'))
# find latin words embedded in Chinese text that look like accidental English artifacts
bad = re.compile(r'[A-Za-z]{3,}')
for x in a:
    for k in ('s', 'bio'):
        for m in bad.finditer(x.get(k, '')):
            seg = x[k][max(0, m.start()-14):m.end()+14]
            print(x['id'], k, repr(seg))
    for k in ('al', 'ro'):
        v = x.get(k, '')
        if bad.search(v):
            print(x['id'], k, repr(v))
