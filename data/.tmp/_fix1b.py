import io, json
path = 'data/.tmp/figdata_fill1.json'
s = io.open(path, encoding='utf-8').read()
reps = [
    ('赵zee之战为鉴', '赵之战为鉴'),
    ('力主「延Moreno边之外，而不敢内」', '力主「拓边之外而不敢轻内」'),
    ('因 dynastic 劳积累劳致病', '因积劳成疾而致病'),
]
for a, b in reps:
    if a in s:
        s = s.replace(a, b)
    else:
        print('NOT FOUND:', a)
io.open(path, 'w', encoding='utf-8', newline='').write(s)
json.load(io.open(path, encoding='utf-8'))
print('ok')
