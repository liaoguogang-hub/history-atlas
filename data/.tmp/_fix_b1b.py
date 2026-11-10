# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b1.py'
s = io.open(p, encoding='utf-8').read()

rep = [
 ('''  "失国后流亡斟鄂一带，王位由其弟仲康暂承"
 ],''',
  '''  "失国后流亡斟鄂一带，王位由其弟仲康暂承",
  "其失国成为夏朝世袭基业第一次中断的标志"
 ],'''),
 ('"summary": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治的政务核心之一。",',
  '"summary": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治中政务中枢之一。",'),
 ('"summary": "唐代高僧，六次东渡日本传戒律，双目失明仍不改初志，是日本律宗的初祖。",',
  '"summary": "唐代高僧，六次东渡日本传戒律，双目失明仍不改初志，被尊为日本律宗初祖。",'),
 ('"summary": "唐代现实主义诗圣，一生漂泊困顿而以诗记录时代乱离，其诗因而被称诗史。",',
  '"summary": "唐代现实主义诗圣，一生漂泊困顿而以诗记录时代乱离，其诗因而被称为诗史。",'),
]

for a, b in rep:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
