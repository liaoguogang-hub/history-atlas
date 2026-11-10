# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b3.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
 ('与诸子约法曰「-make 百姓无得藏金帛，子孙可保家」',
  '与诸子约法曰「百姓无得藏金帛，子孙可保家」'),
 ('开封人刘 Zah 远曾问其入主之由', '开封人曾问其入主之由'),
 ('他还严禁官员为贪，PALETTE 巡按诸道', '他还严禁官员为贪，巡按诸道'),
 ('作言曰「陛下 Spirited 不恤外人，专以己急」',
  '作言曰「陛下不恤外人，专以己急」'),
 ('梁州定难军节度使唐Fibonacci克竟解围', '梁州定难军节度使唐克让竟解围'),
 ('又尽诛朝士，掘太原 commuter 陵以绝其祀', '又尽诛朝士，掘太原诸陵以绝其祀'),
 ('"alias": "朱全忠、-points 朱温",', '"alias": "朱全忠",'),
 ('伏兵于 talent 内侍省下', '伏兵于内侍省下'),
 ('唐初太宗 era 平定吐谷浑、吐蕃之时', '唐初太宗时代平定吐谷浑、吐蕃之时'),
]

for a, b in pairs:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
