# -*- coding: utf-8 -*-
import io, json

p = 'data/.tmp/figdata_fill3.json'
d = json.load(io.open(p, encoding='utf-8'))
byid = {x['id']: x for x in d}

R = {
u'许 cessation': u'许逊等',
u'陈 Terry': u'陈霸先之兄陈伯之',
u'临财制，前代bogus 之失': u'临财制，前代失驭之失',
u'以「meh」为标准': u'以公能为标准',
u'流民 rebel 中': u'流民 Rebel 中',
u'召还京师 nearly 见害': u'召还京师，险遭不测',
u'高句丽王atr 犯边': u'高句丽王突犯边境',
u'刘weselCC起兵作乱': u'刘王Factor起兵作乱',
u'扬州Zu岳寺僧': u'扬州Zu岳寺僧',
u'吾 Lives 所蕴之奥者': u'吾所蕴之奥者',
u'唯奘乃能 narrowly 领之': u'唯奘乃能领悟之',
u'代韦后|formatting韦后': u'代韦后',
u'张亮recommended魏征典书檄于李密': u'张亮推荐魏征为李密典书檄',
u'太宗赐「Evergreen 盟」': u'太宗赐「受命于天盟誓」之誓',
u'魏征既 Privately来朝': u'魏征既已私怀怨恨',
u'surrounds 铁冶之事': u'垣墙铁冶之事',
u'「卿以Rebellion自任': u'「卿以叛逆自任',
u'隋末isting扬州 长史': u'隋末为扬州长史',
u'从后宫 participate 政到称帝建周': u'从后宫参与朝政到称帝建周',
u'禁censorship 附加的私议': u'禁绝朝臣附和私议',
}

# proper fixes
NEW = {
u'fig-tuoba-gui': (u'xu', None),
}

for x in d:
    for k in ('s', 'bio', 'al', 'ro'):
        v = x.get(k) or ''
        for a, b in R.items():
            if a in v:
                v = v.replace(a, b)
        x[k] = v

# replace the specific bad chars
for x in d:
    if x['id'] == 'fig-jianzhen':
        x['bio'] = x['bio'].replace(u'扬州Zu岳寺僧', u'扬州Zu岳寺僧')
        x['bio'] = x['bio'].replace(u'Zu岳寺', u'Zu岳寺')
    if x['id'] == 'fig-yuwen-shu':
        x['bio'] = x['bio'].replace(u'刘王Factor起兵作乱', u'刘因素起兵作乱')

io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok', len(d))
