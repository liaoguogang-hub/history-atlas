import io, json, sys, os, tempfile

MAIN = 'data/.tmp/figdata_fill2.json'
MINE = 'data/.tmp/_mine.json'

# load mine (authoritative, private)
mine = json.load(io.open(MINE, encoding='utf-8'))

# load existing fill2 if present
try:
    existing = json.load(io.open(MAIN, encoding='utf-8'))
except Exception:
    existing = []

merged = {}
order = []
for it in existing + mine:
    i = it.get('id')
    if not i:
        continue
    if i not in merged:
        order.append(i)
    merged[i] = it  # mine wins on duplicate

out = [merged[i] for i in order]
tmp = MAIN + '.tmp'
with io.open(tmp, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
os.replace(tmp, MAIN)
print('fill2 total', len(out))
