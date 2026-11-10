import json
p = 'data/.tmp/world_events_b2.json'
d = json.load(open(p, encoding='utf-8'))

PATCH = {
 "ev-isl-ibn-battuta-travel": {"p":"w-renaissance","y":1325,"ye":1354},
 "ev-isl-ibn-khaldun-muqaddimah": {"p":"w-renaissance","y":1377,"ye":1377},
 "ev-med-euro-100-years-war": {"p":"w-renaissance","y":1337,"ye":1453},
 "ev-med-euro-black-death": {"p":"w-renaissance","y":1347,"ye":1353},
 "ev-med-cn-compass": {"p":"w-spring-autumn","y":-300,"ye":-221,"dt":"公元前300年－公元前221年"},
 "ev-med-sea-angkor": {"p":"w-post-roman-asia","y":802,"ye":999,"dt":"公元802年－公元999年"},
 "ev-med-sea-malacca": {"p":"w-post-roman-asia","y":671,"ye":999,"dt":"公元671年－公元999年"},
 "ev-med-sea-polynesia": {"p":"w-renaissance","y":1200,"ye":1600,"dt":"公元1200年－公元1600年"},
}
n=0
for it in d:
    if it['id'] in PATCH:
        it.update(PATCH[it['id']]); n+=1
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', n)
