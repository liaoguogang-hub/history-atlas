import io, json
p = 'data/.tmp/figdata_fill2a.json'
s = io.open(p, encoding='utf-8').read()
s = s.replace('"by":null",', '"by":null,')
io.open(p, 'w', encoding='utf-8', newline='').write(s)
d = json.loads(io.open(p, encoding='utf-8').read())
print('OK', len(d))
