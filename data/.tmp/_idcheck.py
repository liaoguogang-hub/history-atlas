import io, json
p = 'data/.tmp/missing_figure_ids.json'
raw = io.open(p, encoding='utf-8', errors='replace').read()
seg = raw[raw.find('cn-nanbei-north'):raw.find('cn-tang-early')]
import re
for x in re.findall(r'"(fig-[^"]*)"', seg):
    print(x, [hex(ord(c)) for c in x])
print('---- full json loads with replace ----')
raw2 = io.open(p, encoding='utf-8', errors='replace').read()
d = json.loads(raw2)
for x in d['cn-nanbei-north']:
    print(repr(x), [hex(ord(c)) for c in x])
