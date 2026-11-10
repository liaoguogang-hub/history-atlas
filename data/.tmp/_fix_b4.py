# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b4.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
 ('又有《景德新 records》以记时事', '又有《景德新编》以记时事'),
 ('斩 thermally 违纪将，以振军心', '斩违纪将，以振军心'),
 ('宋军「Composer」欢声动地', '宋军欢声动地'),
 ('昇 death 不禁曰', '昇不禁曰'),
 ('强调词有别于诗文的一声一 nuances 音律特色', '强调词有别于诗文的一声一调之音律特色'),
 ('以「 DQ 众，吾已脱身矣」之语相嘱', '以「众吾已脱身矣」之语相嘱'),
 ('此乃Heavenly 遣将也', '此乃天遣将也'),
 ('他亦 actively 倡修《四书》《五经》之书', '他亦积极倡修《四书》《五经》之书'),
 ('以「perturb 众」为号', '以「扰众」为号'),
]

for a, b in pairs:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
