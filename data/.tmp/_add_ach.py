# -*- coding: utf-8 -*-
"""把缺失的成就条目正确追加到 achievements 数组末尾。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

ACH = {
 "fig-qian-hongchu": ["境内虽小而安，士人得以避乱业"],
 "fig-wang-yanzheng": ["为后周南征北伐的主要宿将之一"],
 "fig-shang-rang": ["为贯穿黄巢起义始终的核心将领"],
 "fig-zhang-zhuo": ["其名见晚唐藩镇与农民战争的零星记载"],
 "fig-zhou-chang": ["与汪世显同为陕甘汉军将领"],
 "fig-tian-xiang-2": ["唐初将门承袭之制的代表人物"],
 "fig-li-ai": ["其名见昭宗哀宗纪及唐末诸将列传"],
 "fig-wu-daozi": ["杜甫诗赞其画为观其妙笔天落落"],
 "fig-li-guangbi": ["广德元年病逝于徐州，赠太尉，谥号武"],
 "fig-zhu-wu-zhong": ["朱氏累世掌兵河东，是唐室倚为屏藩的一支将门力量"],
 "fig-li-de": ["整理修订律令，为宣宗朝慎断狱提供制度保障"],
 "fig-li-heng": ["卒于镇，赠太尉，谥号忠武"],
 "fig-wu-daozi-2": ["草书上承二王而下启黄庭坚，为狂草一脉的关键人物"],
 "fig-li-jiancheng": ["与齐王李元吉结党，多次谋害李世民"],
 "fig-li-shimin": ["贞观二十三年崩于翠微宫，谥号文皇帝，庙号太宗，葬昭陵"],
 "fig-wu-zetian": ["705年神龙政变后退位，与高宗合葬乾陵，墓前立无字碑"],
 "fig-dai-rene": ["卒于洛阳，赠尚书右仆射，谥号文献"],
 "fig-xuanzang": ["所译《瑜伽师地论》八百卷，为汉译佛典中卷帙最巨者"],
 "fig-jianzhen": ["日本于奈良唐招提寺建墓纪念，成为中日文化交流的象征"],
 "fig-li-bai": ["后世编有《李太白集》三十卷传世"],
 "fig-du-fu": ["与李白并称李杜，为唐诗双子座"],
 "fig-bai-juyi": ["编《白氏长庆集》七十五卷，为其一生诗作的总集"],
 "fig-yuan-zhen": ["元稹与白居易并称元白，与韩柳并峙于中唐文坛"],
 "fig-liu-yu": ["与白居易并称刘白，为中唐诗坛两大流派之一"],
 "fig-wang-changling": ["安史之乱中不肯附逆，被诬陷杀害"],
 "fig-an-lushan": ["其乱后唐朝无力控制藩镇，藩镇割据之势自此成形"],
 "fig-shi-sim": ["有穷氏部众在其后遭寒浞诛灭，政权旋起旋灭"],
 "fig-yang-guozhong": ["马嵬驿兵变中被乱军诛杀，其子杨暄亦死于乱兵"],
 "fig-yang-guifei": ["杜甫《哀江头》《北征》等诗写战乱中帝妃出逃之状"],
 "fig-liu-zongyuan": ["《旧唐书》称其文章雄深雅健，宋人称其寄至味于澹泊"],
 "fig-han-yu": ["位列唐宋八大家之首，影响明清文坛数百年"],
 "fig-yan-zhenqing": ["《祭侄文稿》被誉为天下第二行书"],
 "fig-guo-ziyi": ["官至太尉、中书令，封汾阳郡王，为唐代武将人格典范"],
 "fig-li-de": ["以清廉自守，在酷吏政治时期为武周朝堂保留清流"],
 "fig-li-heng": ["任唐随邓州节度使，治军有法，深得军心"],
 "fig-li-jiancheng": ["武德九年玄武门之变中被李世民射杀"],
 "fig-wu-yue": ["宋初纳土归宋，为五代政权中难得的善终者"],
 "fig-li-bian": ["在位十一年，其后子李璟即位"],
 "fig-li-yu": ["以切身的君国之痛开启宋词婉约一脉，影响后世极深"],
 "fig-liu-zhiyuan": ["后汉速亡于郭威兵变，五代武人政权的困局由此显现"],
 "fig-guo-wei": ["为北宋统一奠定基础，后世为赵匡胤所效法"],
 "fig-stone-jingmao": ["燕云十六州之割成为北宋百余年边患之源"],
 "fig-chao-rong": ["为北宋统一奠定基础，其所立法令多被宋朝承袭"],
 "fig-li-chang-tang": ["与后晋高祖石敬瑭并称五代较有作为的君主"],
 "fig-liwang-yan": ["宠倖伶人、聚敛民财而亡政，成为五代武人政权失政的典型"],
 "fig-li-conghou": ["被李从珂派人缢杀，年仅二十二岁"],
 "fig-zhu-ci-2": ["泾原兵变为唐代中期规模最大的内乱之一，唐廷元气大伤"],
 "fig-li-zhu": ["908年被毒杀，年仅十七岁"],
 "fig-luo-hongxin": ["魏博成为朱温在河北的重要屏障，为其统一中原提供助力"],
 "fig-shang-rang": ["884年黄巢军溃败后投降时溥，随即被杀"],
 "fig-zhang-zhuo": ["本条依原始资料保留，以存晚唐武将群体史迹之全"],
 "fig-nanbei-north-zhou-wu": ["对宋代宫廷画院与明清工笔人物画影响深远"],
 "fig-huang-chao": ["所作菊花诗传诵千古，抒发反抗者情怀"],
 "fig-zhu-wen": ["晚年与诸子争权，912年被亲子朱友珪弑杀"],
 "fig-pu-gu-huai-en": ["与郭子仪交谊笃厚，其子娶郭氏女"],
 "fig-yu-chao-en": ["783年被李晟浑瑊设计诛杀，宦官势力为之一挫"],
 "fig-zhou-chang": ["以汉地武力襄助蒙古经略中原，沟通了军事传统与新兴政权"],
 "fig-tian-xiang-2": ["为唐初将门承袭之制的代表人物之一"],
 "fig-li-ai": ["本条依原始资料保留，以存晚唐武将群体史迹之全"],
}


def add_all(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    for fid, texts in ACH.items():
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"achievements": \[', s[m.end():])
        if not m2:
            continue
        k = m.end() + m2.end()
        # 找匹配的 ]
        depth = 1
        i = k
        while i < len(s):
            c = s[i]
            if c == '"':
                i += 1
                while i < len(s) and s[i] != '"':
                    if s[i] == '\\':
                        i += 1
                    i += 1
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        # i 指向 ]
        j = s.rfind('\n', k, i)
        block = ''.join('  "%s",\n' % t for t in texts)
        # 去掉最后一个逗号
        block = block.rstrip(',\n') + '\n'
        s = s[:j + 1] + block + s[j + 1:]
    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    if add_all(p):
        print('patched', fn)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
