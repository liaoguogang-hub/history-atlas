import json
p = 'data/.tmp/world_events_b3.json'
d = json.load(open(p, encoding='utf-8'))

PATCH = {
 "ev-ren-gutenberg-printing": {"p":"w-italian-renaissance","y":1450,"ye":1455},
 "ev-ren-printing-incunabula": {"p":"w-italian-renaissance","y":1465,"ye":1499,"dt":"公元1465年－公元1499年"},
 "ev-ren-leibniz-calculus": {"p":"w-scientific-revolution","ye":1700,"dt":"公元1676年－公元1700年"},
 "ev-discover-magellan-circumnav": {"p":"w-northern-renaissance","y":1519,"ye":1522},
 "ev-discover-mesopotamian-america": {"p":"w-prehistory","y":-3500,"ye":-500,"dt":"公元前3500年－公元前500年"},
 "ev-discover-philippine-galleon": {"p":"w-renaissance","y":1571,"ye":1600,"dt":"公元1571年－公元1600年"},
 "ev-discover-mercantilism": {"p":"w-renaissance","y":1500,"ye":1600,"dt":"公元1500年－公元1600年"},
 "ev-discover-ottoman-empire": {"p":"w-medieval-islam","ye":1300,"dt":"公元1299年－公元1300年"},
 "ev-discover-mughal-empire": {"p":"w-renaissance","y":1526,"ye":1600,"dt":"公元1526年－公元1600年"},
 "ev-discover-ching-ming-qing": {"p":"w-cn-ming","ye":1644,"dt":"公元1368年－公元1644年"},
 "ev-discover-ming-qing-kaifeng-tianxia": {"p":"w-cn-ming","ye":1644,"dt":"公元1368年－公元1644年"},
 "ev-discover-oceania-aboriginal": {"p":"w-prehistory","y":-50000,"ye":-3600,"dt":"公元前50000年－公元前3600年"},
 "ev-discover-nz-maori": {"p":"w-medieval","y":1250,"ye":1300,"dt":"公元1250年－公元1300年"},
 "ev-discover-hawaii-kapu": {"p":"w-medieval","y":1200,"ye":1300,"dt":"公元1200年－公元1300年"},
 "ev-discover-africa-coast-trade": {"p":"w-africa-west","ye":1599,"dt":"公元1440年－公元1599年"},
 "ev-discover-africa-ethiopia-portuguese": {"p":"w-africa-east","ye":1599,"dt":"公元1490年－公元1599年"},
 "ev-discover-iberia-silver": {"p":"w-renaissance","y":1545,"ye":1600,"dt":"公元1545年－公元1600年"},
 "ev-discover-price-revolution": {"p":"w-renaissance","y":1500,"ye":1600,"dt":"公元1500年－公元1600年"},
 "ev-discover-triangle-trade": {"p":"w-renaissance","y":1562,"ye":1600,"dt":"公元1562年－公元1600年"},
 "ev-discover-haiti-revolution": {"p":"w-absolute-monarchy","c":"political","y":1791,"ye":1800,"dt":"公元1791年－公元1800年"},
 "ev-discover-india-british-east-india": {"p":"w-early-modern","y":1600,"ye":1749,"dt":"公元1600年－公元1749年"},
 "ev-discover-africa-slave-route-madagascar": {"p":"w-africa-east","ye":1599,"dt":"公元1500年－公元1599年"},
 "ev-discover-latitude-decline": {"p":"w-early-modern","c":"economic","y":1660,"ye":1749,"dt":"公元1660年－公元1749年"},
 "ev-discover-inquisition-philippines": {"p":"w-renaissance","y":1565,"ye":1600,"dt":"公元1565年－公元1600年"},
 "ev-discover-silk-road-persian": {"p":"w-renaissance","y":1501,"ye":1600,"dt":"公元1501年－公元1600年"},
 "ev-discover-guatemala-filipino": {"p":"w-renaissance","y":1565,"ye":1600,"dt":"公元1565年－公元1600年"},
}
n=0
for it in d:
    if it['id'] in PATCH:
        it.update(PATCH[it['id']]); n+=1
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', n)
