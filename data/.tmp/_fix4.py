import io, re, sys

p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()

fixes = [
    ("父亦_current 啻 认可", "父亦深奇之"),
    ("陈蕃时在outer 因病在蕃所请疾室，诏书到，蕃起wear 怒曰「何谓反贼！\",拔剑斩数人。",
     "陈蕃时因病在所请疾室，诏书到，蕃起怒曰「何谓反贼」，拔剑斩数人。"),
    ("蕃子陈 Guer 及宾客皆夷诛", "蕃子陈禅及宾客皆夷诛"),
    ("四方贡献，皆不_THIS 上于己。魏文帝遣使三诏 interrogation，献帝三让而后受禅。",
     "四方贡献，皆不上于己。魏文帝遣使三诏册命，献帝三让而后受禅。"),
    ("时任 pipi 失败。166年，皇甫嵩迁长社丞。168年，嵩与长社丞、破羌校尉等共平波才等。",
     "时任长社丞。166年，皇甫嵩迁长社丞。168年，嵩与长社丞、破羌校尉等共平波才等。"),
    ("其自 conduct 严 苛 以 绳下，常以「天下楷模李元礼」为名。",
     "其自处严苛以绳下，常以「天下楷模李元礼」为名。"),
    ("张角与弟张宝、张梁皆能辟五斗米道，cheme 率弟子传道四方。",
     "张角与弟张宝、张梁皆能辟五斗米道，cheme以符水咒说，率弟子传道四方。"),
    ("献策���-制孙权，谓「孙权新起，江东未固」不宜急攻。",
     "献计劝阻曹操南攻，谓「孙权新起，江东未固」不宜急攻。"),
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
