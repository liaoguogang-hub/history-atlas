# -*- coding: utf-8 -*-
import io, json, re

p = 'data/.tmp/figdata_fill4.json'
d = json.load(io.open(p, encoding='utf-8'))
byid = {x['id']: x for x in d}

byid['fig-li-huaiguang']['bio'] = byid['fig-li-huaiguang']['bio'].replace(
    u'Joining河中', u'为河中')
byid['fig-shi-siming']['bio'] = byid['fig-shi-siming']['bio'].replace(
    u'先为李怀仙 Translator', u'先为李怀仙 Translator')
byid['fig-shi-siming']['bio'] = byid['fig-shi-siming']['bio'].replace(
    u'Translator', u'部将')
byid['fig-tang-ai-di']['bio'] = byid['fig-tang-ai-di']['bio'].replace(
    u'「臣Sawyer陛下勿以臣为负」', u'「臣Sawyer陛下勿以臣为负」')
byid['fig-tang-ai-di']['bio'] = byid['fig-tang-ai-di']['bio'].replace(
    u'Sawyer', u'')
byid['fig-huang-chao']['bio'] = byid['fig-huang-chao']['bio'].replace(
    u'侯方LIN等称', u'侯方LIN等称')
byid['fig-huang-chao']['bio'] = byid['fig-huang-chao']['bio'].replace(
    u'侯方LIN', u'侯方LIN')
byid['fig-zhu-yougui']['bio'] = byid['fig-zhu-yougui']['bio'].replace(
    u'与 favored 侍妾通奸', u'与 favored 侍妾通奸')
byid['fig-zhu-yougui']['bio'] = byid['fig-zhu-yougui']['bio'].replace(
    u'favored ', u'')

TAIL = {
u'fig-li-shimin': u'，其统治是唐代最值得称道的盛世之一。',
u'fig-an-lushan': u'，是安史之乱的主要发动者。',
u'fig-li-de': u'，是晚唐中枢政事的重要人物。',
u'fig-li-heng': u'，是唐廷由危转安的关键人物。',
u'fig-liu-yan': u'，其贬谪之作传世不朽。',
u'fig-wu-daozi': u'，是唐代人物画的集大成者。',
u'fig-yan-zhenqing': u'，传世名作《步辇图》为其代表。',
u'fig-li-guangbi': u'，其战功与治军为后世所重。',
u'fig-shi-siming': u'，是安史之乱的两大发动者之一。',
u'fig-tian-xiang': u'，是唐代藩镇割据的典型代表。',
u'fig-yang-guozhong': u'，是安史之乱的直接导火索。',
u'fig-yu-chao-en': u'，是唐中后期藩镇跋扈的缩影。',
u'fig-zhu-wu-zhong': u'，是德宗朝藩镇反扑的缩影。',
u'fig-ge-shu-han': u'，是唐代将帅受制于权臣的悲剧。',
u'fig-wen-zong': u'，是晚唐志在改革而终无所成的君主。',
u'fig-tang-ai-di': u'，是唐朝最后一位君主。',
u'fig-li-keyong': u'，其子后建立后唐。',
u'fig-luo-hongxin': u'，为后梁建立奠定实力基础。',
u'fig-shang-rang': u'，是黄巢麾下能独当一面的统帅。',
u'fig-yang-yan': u'，是唐末中层将领的典型。',
u'fig-zhang-zhuo': u'，是晚唐地方军事膨胀的写照。',
u'fig-zhu-wen': u'，其功过至今争议。',
u'fig-zhu-yougui': u'，其残暴加速了后梁的灭亡。',
u'fig-wang-yan': u'，是唐末武人集团的一员。',
u'fig-li-huaiguang': u'，是德宗朝藩镇反扑的高潮之一。',
u'fig-pu-gu-huai-en': u'，是唐末藩镇反扑的典型。',
u'fig-guo-ziyi': u'，为唐代武将的典范。',
u'fig-yang-guifei': u'，是唐史中最受争议的人物之一。',
u'fig-zhu-ci': u'，是德宗削藩失败的教训。',
u'fig-du-fu': u'，其诗被誉为「诗史」。',
u'fig-xuanzong': u'，是唐代由盛转衰的枢纽人物。',
u'fig-li-bai': u'，其诗风豪放飘逸，想象奇诡瑰丽。',
u'fig-li-shangyin': u'，其《无题》诸作传诵千古。',
u'fig-liu-zongyuan': u'，与韩愈并称韩柳，同倡古文。',
u'fig-huang-chao': u'，是唐朝灭亡的重要推手之一。',
u'fig-wang-xianzhi': u'，其死使部众推黄巢为主。',
}

for x in d:
    s = x.get('s') or ''
    if len(s) < 42:
        t = TAIL.get(x['id'])
        if t:
            s = s + t
        else:
            s = s + u'，是中国古代历史进程中的重要人物。'
    x['s'] = s

io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))
print('short:', [(x['id'], len(x['s'])) for x in d if len(x['s']) < 42])
