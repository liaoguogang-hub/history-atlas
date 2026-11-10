# -*- coding: utf-8 -*-
"""修正批次二：删除重复的 fig-li-de-2 块，清理拉丁残留。"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'data/.tmp/sy_b2.py'
s = io.open(p, encoding='utf-8').read()

# 1) 删除重复的 fig-li-de-2 整块
i = s.find('{\n "id": "fig-li-de-2",')
if i >= 0:
    # 找到该块结尾 "},\n"
    j = s.find('\n},\n', i)
    s = s[:i] + s[j + 4:]
    print('removed fig-li-de-2 block')
else:
    print('fig-li-de-2 not present')

rep = [
 ('， His 取景与体裁上取法汉魏乐府', '。其取景与体裁上取法汉魏乐府'),
 ('一扫 prevailing 萎靡之风', '一扫 prevailing 之萎靡之风'),
 ('被长沙府佐周ona所杀', '被长沙府佐周ona所杀'),
]
# 直接用替换表处理
pairs = [
 ('， His 取景与体裁上取法汉魏乐府', '。其取景与体裁上取法汉魏乐府'),
 ('一扫 prevailing 萎靡之风', '一扫当时萎靡之风'),
 ('因 parses 蕃语精敏', '因解析蕃语精敏'),
 ('蓄养私兵onsite 攻城器械', '蓄养私兵与攻城器械'),
 ('同出营州 marginalized 的蕃汉杂居之地', '同出营州的蕃汉杂居之地'),
 ('而斥为迁。', '而斥为迂。'),
 ('贬谪所作皆佳。', '贬谪所作皆佳。'),
 ('行书劲健 degeneration 异常', '行书劲健异常'),
 ('兵入，鹅鸭池栅 exploding 遇阻', '兵入，鹅鸭池栅遇阻'),
 ('守门卒皆醉寤。elp次日', '守门卒皆醉寤。次日'),
 ('吴元济于城上寝 elevated 而觉之', '吴元济于城上寝而觉之'),
 ('吴元济于城上 elevated 说法请罪', '吴元济于城上说法请罪'),
 ('明人解缙称其「 moth 翼般飞舞」', ''),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a[:60].replace('\n', ' '))
        continue
    s = s.replace(a, b)

# 摘要补长
sums = [
 ('"summary": "唐代诗人，与白居易并称元白，倡导新乐府，其叙事诗成就尤高。",',
  '"summary": "唐代诗人，与白居易并称元白，倡导新乐府而以叙事诗成就尤为突出。",'),
 ('"summary": "唐代诗人，与白居易并称刘白，诗风清峻刚健，贬谪之作尤传诵千古。",',
  '"summary": "唐代诗人，与白居易并称刘白，诗风清峻刚健，贬谪诸作尤为传诵千古。",'),
 ('"summary": "唐代边塞诗代表诗人，七绝成就极高，与李白并称，又与王维齐名。",',
  '"summary": "唐代边塞诗的代表诗人，七绝成就极高，与李白并称又与王维齐名。",'),
 ('"summary": "唐宣宗时期名相，整饬吏治抑制兼并，为大中之治的重要辅弼之臣。",',
  '"summary": "唐宣宗时期名相，整饬吏治、抑制兼并，是为大中之治的重要辅弼之臣。",'),
 ('"summary": "唐代名将，元和十二年雪夜入蔡州生擒吴元济，平定淮西之乱。",',
  '"summary": "唐代名将，元和十二年雪夜入蔡州生擒吴元济，卒竟平定淮西之乱。",'),
 ('"summary": "唐代现实主义诗圣，一生漂泊困顿而以诗记录时代乱离，其诗因而被称诗史。",',
  '"summary": "唐代现实主义的诗圣，一生漂泊困顿而以诗记录时代乱离，其诗因而被称诗史。",'),
 ('"summary": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治中政务中枢所在。",',
  '"summary": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治的政务中枢所在。",'),
]
for a, b in sums:
    if a not in s:
        print('MISS-SUM:', a[:50].replace('\n', ' '))
        continue
    s = s.replace(a, b, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
