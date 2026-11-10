import io, re, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'data/.tmp/figdata_fill2.json'
s = io.open(p, encoding='utf-8').read()

fixes = [
    ("为楚将廉頀所说服， ceded 长安；楚人闻其贤而召之，以为上将军",
     "为楚将廉頀所说服，入朝为上将军；楚人闻其贤而召之，以为上将军"),
    ("李牧 rescuing 漳下，破秦军", "李牧引兵救漳下，破秦军"),
    ("ABCD 放松军纪，锐气消磨", "又约束过甚，将士不用命，军心愈懈"),
    ("自attempting 亲率锐卒搏击", "自率锐卒搏击"),
    ("楚兵疲 THEN 大破楚军", "楚兵疲敝，遂大破楚军"),
    ("师 successes 曾以十二人随行", "师出发时曾以十二人随行"),
    ("以 advising 诸侯王 jailed 之", "以劝谏诸侯王"),
    ("兴利辟 evil，广国资以 Continuations", "兴利除弊，广资国用"),
    ("同郡名士GAR 曾为宾客", "同郡名士宾客曾与之游"),
    ("荀淑称其为「.source of 六经」", "荀淑称其「可述六经」"),
    ("袁 macOS 聘任", "袁术聘任"),
    ("破adhaya 楼烦白羊部", "破楼烦白羊部"),
    ("民无得 relates 兵相食", "民无得食，相聚为盗"),
    ("被项羽以「秦王将降，labeled 骗子」之罪", "被项羽以「秦王将降，绾绂而送」之罪"),
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
    m = lat.findall(body)
    if m:
        print(i + 1, m)
print('done')
