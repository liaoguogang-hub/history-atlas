# -*- coding: utf-8 -*-
import io, json, re, sys, glob

def fix(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    # "-?," -> null,   "-?}" -> null
    s = s.replace('"-?",', '"by":null,')
    s = s.replace('"by":-?",', '"by":null,')
    s = s.replace('"dy":-?",', '"dy":null,')
    # generic: "key":-?  ->  "key":null
    s = re.sub(r'("(?:by|dy)":)-?\?', r'\1null', s)
    if s != orig:
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
    try:
        d = json.loads(io.open(path, encoding='utf-8').read())
        print(path, 'OK', len(d))
        return True
    except Exception as e:
        print(path, 'FAIL', e)
        return False

for f in sys.argv[1:]:
    fix(f)
