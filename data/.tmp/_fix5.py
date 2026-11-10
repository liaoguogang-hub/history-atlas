import io, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()

fixes = [
    ('陈蕃时在outer 因病在蕃所请疾室，诏书到，蕃起wear 怒曰「何谓反贼！\\",拔剑斩数人。',
     '陈蕃时因病在所请疾室，诏书到，蕃起怒曰「何谓反贼」，拔剑斩数人。'),
    ('张角与弟张宝、张梁皆能辟五斗米道，cheme以符水咒说，率弟子传道四方。',
     '张角与弟张宝、张梁皆能辟五斗米道，cheme以符水咒说，率弟子传道四方。'),
]
for a, b in fixes:
    if a in s:
        s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)

lat = re.compile(r'[A-Za-z]{2,}')
for i, l in enumerate(s.split('\n')):
    body = re.sub(r'"(id|n|al|by|dy|lt|ro|p|g|bio|ac|q|re|rf|t)":', '', l)
    body = re.sub(r'fig-[a-z0-9-]+', '', body)
    body = re.sub(r'ev-[a-z0-9-]+', '', body)
    body = re.sub(r'cn-[a-z0-9-]+', '', body)
    body = re.sub(r'\b(male|female|unknown|null)\b', '', body)
    body = re.sub(r'[^\u3000-\u9fff\uff00-\uffef]', '', body)
    m = lat.findall(body)
    if m:
        print(i + 1, m)
print('done')
