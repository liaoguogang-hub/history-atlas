# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b4.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
 ('不费岁币而Peace 百年', '不费岁币而得百年之安'),
 ('昇 death 不禁日：', '昇不禁曰：'),
 ('一以 restores 复为主', '一以恢复为主'),
 ('列阵 challenge，岳飞以步兵', '列阵挑战，岳飞以步兵'),
]

for a, b in pairs:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
