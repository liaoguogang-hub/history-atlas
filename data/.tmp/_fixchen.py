# -*- coding: utf-8 -*-
import io, json
p = 'data/.tmp/figdata_fill2a.json'
d = json.load(io.open(p, encoding='utf-8'))
for x in d:
    if x['id'] == 'fig-chen-qun':
        x['bio'] = x['bio'].replace(
            u'刘备问「臧君高视万物」，先主亦以卿为方之 man 属。汉末陈群避乱淮南，曾劝袁术称帝不成。',
            u'刘备问其识人之能，先主亦盛称其有知人之明。曹丕即位后，陈群又被召为御史中丞，转为尚书。')
        x['bio'] = x['bio'].replace(
            u'曹丕即位，征陈群为御史中丞，转为尚书。曹丕称帝后，与尚书令陈群议九品官人之法',
            u'曹丕称帝后，与尚书令陈群议九品官人之法')
io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok')
