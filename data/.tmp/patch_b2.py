import json
p = 'data/.tmp/world_events_b2.json'
d = json.load(open(p, encoding='utf-8'))

PATCH = {
 "ev-isl-umayyad-iberia": {"p":"w-post-roman-europe","ye":750,"dt":"公元711年－公元750年"},
 "ev-isl-ibn-battuta-travel": {"p":"w-post-70s","y":1325,"ye":1354},
 "ev-isl-ibn-khaldun-muqaddimah": {"p":"w-post-70s","y":1377,"ye":1377},
 "ev-mongol-pax-mongolica-detail": {"p":"w-mongol-empire","ye":1300,"dt":"公元1220年－公元1300年"},
 "ev-med-euro-feudalism": {"p":"w-medieval","y":1000,"ye":1200,"dt":"公元1000年－公元1200年"},
 "ev-med-euro-viking": {"p":"w-post-roman-europe","ye":999,"dt":"公元793年－公元999年"},
 "ev-med-euro-hagia-sophia-1204": {"p":"w-byzantium","ye":1300,"dt":"公元1000年－公元1300年"},
 "ev-med-euro-100-years-war": {"p":"w-post-70s","y":1337,"ye":1453},
 "ev-med-euro-black-death": {"p":"w-post-70s","y":1347,"ye":1353},
 "ev-med-cn-song-commerce": {"p":"w-medieval-china","y":1000,"ye":1279,"dt":"公元1000年－公元1279年"},
 "ev-med-cn-compass": {"p":"w-cn-han","y":-300,"ye":-100,"dt":"公元前300年－公元前100年"},
 "ev-med-sea-angkor": {"p":"w-ming-qing","y":802,"ye":1431},
 "ev-med-sea-malacca": {"p":"w-ming-qing","y":671,"ye":1433},
 "ev-med-sea-polynesia": {"p":"w-early-modern","y":1200,"ye":1600,"dt":"公元1200年－公元1600年"},
}
n=0
for it in d:
    if it['id'] in PATCH:
        it.update(PATCH[it['id']]); n+=1
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', n)
