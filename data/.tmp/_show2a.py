# -*- coding: utf-8 -*-
import io, json
p = 'data/.tmp/figdata_fill2a.json'
d = json.load(io.open(p, encoding='utf-8'))
ids = ['fig-liu-bei','fig-zhuge-liang','fig-jiang-wei','fig-zhang-yue','fig-deng-ai','fig-zhuge-shang','fig-chen-qun','fig-gongsun-yuan','fig-yu-jin','fig-cao-huang','fig-han-emperor-mingdi','fig-liu-mao','fig-liu-yao','fig-sima-de','fig-sima-jiong','fig-sima-ying','fig-sima-yue','fig-liuyuan','fig-li-yun','fig-yang-jian','fig-liu-xie']
buf = []
for x in d:
    if x['id'] in ids or '尔朱荣' in x['id']:
        buf.append('=== ' + x['id'])
        buf.append('S: ' + x.get('s',''))
        buf.append('BIO: ' + x.get('bio',''))
        buf.append('')
io.open('data/.tmp/_review2a.txt','w',encoding='utf-8').write('\n'.join(buf))
print('written', len(buf))
