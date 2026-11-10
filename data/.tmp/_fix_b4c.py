# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b4.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
 ('能制 wines 为饮', '能酿酒为饮'),
 ('擒其王大asserlite，以其地为东丹国', '擒其王大耆望，以其地为东丹国'),
 ('号太宗。\',\n "achievements": [\n  "907年统一契丹各部称王',
  '号太宗。",\n "achievements": [\n  "907年统一契丹各部称王'),
]

for a, b in pairs:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
compile(s, p, 'exec')
print('done, syntax ok')
