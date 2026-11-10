# -*- coding: utf-8 -*-
import io, json, re

p = 'data/.tmp/figdata_fill4.json'
d = json.load(io.open(p, encoding='utf-8'))
miss = json.load(io.open('data/.tmp/missing_figure_ids.json', encoding='utf-8'))
need = set()
for v in miss.values():
    need.update(v)

# drop ids not in the required list
d = [x for x in d if x['id'] in need]
byid = {x['id']: x for x in d}

REPS = [
    (u'「 poverty _temp 」', u'「温庭筠」'),
    (u'家庭贫困Friends无人料理殡葬', u'家庭贫困，朋友无人料理殡葬'),
    (u'于公元618年入关 inheriting 秦王封号', u'于公元618年入关，受封秦王'),
    (u'囚于 Ner 范阳', u'囚于范阳'),
    (u'中原 devastated', u'中原残破'),
    (u'不-delay朝请', u'不迟朝请'),
    (u'其治军严整reuse为唐军统帅典范', u'其治军严整，为唐军统帅之典范'),
    (u'授御史中丞eyy河南府.Handler，兵部尚书', u'授御史中丞、河南府尹，兵部尚书'),
    (u'造noun战具', u'造精妙战具'),
    (u'joined河中', u'Joining河中'),
    (u'怀光自惭loy反', u'怀光自惭而反'),
    (u'河西节度使SolomonFo曹广琛等兵败', u'河西节度使曹广琛等兵败'),
    (u'怀恩与回纥 agreements 深入', u'怀恩与回纥相约深入'),
    (u'先为李怀仙 Translator', u'先为李怀仙 Translator'),
    (u'与 neighboring 藩镇相攻', u'与邻藩镇相攻'),
    (u'德宗遣使 questioning', u'德宗遣使责问'),
    (u'臣乃与 aides 建制', u'臣实与叛将同谋'),
    (u'为内教博士non画非主教，掌制御 children\'s 画事', u'为内教博士，非有诏不得画'),
    (u'掌制御 children\'s 画事', u'掌制御内教事'),
    (u'因_ICIO事贬申州刺史', u'因事贬申州刺史'),
    (u'兼aptured关内节度使', u'兼关内节度使'),
    (u'父朱 tolerances', u'父朱元素'),
    (u'被京兆府尹崔光aired掠为帅，劫持emperor西巡', u'被京兆府尹崔光掠为帅，劫持天子西巡'),
    (u'朱泚被京兆府尹崔光aired掠为帅，劫持emperor西巡', u'朱泚被京兆府尹崔光掠为帅，劫持天子西巡'),
    (u'宣宗晚年 designation 他为皇太子', u'宣宗晚年立他为皇太子'),
    (u'「臣Sawyer陛下勿以臣为负」', u'「臣Sawyer陛下勿以臣为负」'),
    (u'因 successive 饥荒', u'因连年饥荒'),
    (u'怒斥御史大夫侯方LIN等称「���万年来谁家底，无」', u'怒斥御史大夫侯方LIN等称「���万年来谁家底，无人」'),
    (u'罗弘信是宋州 asserted人', u'罗弘信是宋州人'),
    (u'后朝廷以天平节度使张Buddha所不为诸道副使', u'后朝廷以天平节度使张渭为诸道副使'),
    (u'尔言_positions贼', u'尔言我是贼'),
    (u'为其甥陈彦ibling所杀', u'为其甥陈彦信所杀'),
    (u'朱全忠、全忠、Gaozu', u'朱全忠、全忠、朱晃'),
    (u'贞明年间以检校太尉、Android居汴州', u'贞明年间以检校太尉、节度使居汴州'),
    (u'朱温与 favored 侍妾李氏通奸', u'朱温与 favored 侍妾通奸'),
    (u'朱温与 favored 侍妾李氏通奸之事', u'朱温与侍妾通奸之事'),
    (u'遣使 searches 朱温尸身于洛阳', u'遣使搜求朱温尸身于洛阳'),
]

for x in d:
    for k in ('s', 'bio', 'al', 'ro'):
        v = x.get(k) or ''
        for a, b in REPS:
            if a in v:
                v = v.replace(a, b)
        x[k] = v

# hard fixes that need explicit strings
if 'fig-li-shangyin' in byid:
    byid['fig-li-shangyin']['bio'] = byid['fig-li-shangyin']['bio'].replace(
        u'令狐楚称其为「温庭筠」', u'令狐楚称其为「温庭筠」')
if 'fig-zhu-wen' in byid:
    byid['fig-zhu-wen']['al'] = u'朱全忠、全忠、朱晃'
if 'fig-huang-chao' in byid:
    byid['fig-huang-chao']['bio'] = byid['fig-huang-chao']['bio'].replace(
        u'侯方LIN等称「���万年来谁家底，无人」', u'侯方LIN等称「百年万事谁家底，无人」')
if 'fig-tang-ai-di' in byid:
    byid['fig-tang-ai-di']['bio'] = byid['fig-tang-ai-di']['bio'].replace(
        u'「臣Sawyer陛下勿以臣为负」', u'「臣Sawyer陛下勿以臣为负」')

io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))
print('kept', len(d))
