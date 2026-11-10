# -*- coding: utf-8 -*-
"""把偏短的 summary 补足到 35-55 字，并修掉剩余拉丁。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

SUM = {
 "fig-du-ru-hui": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治中政务中枢之所在。",
 "fig-yuan-zhen": "唐代诗人，与白居易并称元白，倡导新乐府而以叙事诗的成就尤为突出。",
 "fig-liu-yu": "唐代诗人，与白居易并称刘白，诗风清峻刚健，其贬谪诸作尤为传诵千古。",
 "fig-wang-changling": "唐代边塞诗的代表人物，七绝成就极高，与李白并称又与王维齐名一时。",
 "fig-yang-guifei": "唐玄宗贵妃，善歌舞而通音律，马嵬驿兵变中被迫缢死，遂成盛唐悲剧之象。",
 "fig-liu-zongyuan": "唐代文学家，与韩愈并称韩柳，倡导古文运动，被贬柳州而文名益彰于世。",
 "fig-han-yu": "唐代古文运动的领袖，唐宋八大家之首，以倡儒排佛、文以载道著称于世。",
 "fig-yan-zhenqing": "唐代书法家，创颜体与柳公权并称颜筋柳骨，安史之乱中起兵讨贼不屈被杀。",
 "fig-wu-daozi": "唐代画圣，佛教人物画冠绝一时，笔下衣带飘举，后人称其为吴带当风。",
 "fig-guo-ziyi": "唐代名将，与李光弼共平安史之乱，单骑退回纥，功高而不震主的四朝元老。",
 "fig-li-guangbi": "唐代平定安史之乱的名将，治军严整，太原之战大破史思明而扭转战局。",
 "fig-zhu-wu-zhong": "唐代将领，随父镇守河东而平定安史之乱，代宗时为副元帅率兵收复长安。",
 "fig-li-de": "唐宣宗时期名相，整饬吏治、抑制兼并，是为大中之治的重要辅弼之臣。",
 "fig-li-heng": "唐代名将，元和十二年雪夜入蔡州生擒吴元济，卒竟平定淮西之乱。",
 "fig-wu-daozi-2": "唐代草书名家，与怀素并称张旭怀素，其狂草笔势被后世尊为草圣。",
 "fig-li-jiancheng": "唐高祖长子，号隐太子，参与唐初统一战争，玄武门之变中被李世民射杀。",
 "fig-bai-juyi": "唐代诗人与官员，倡导新乐府运动，《琵琶行》《长恨歌》成为叙事诗的巅峰之作。",
 "fig-shi-sim": "安史之乱主要首领之一，继安禄山后再据洛阳，自称大燕皇帝而终为亲子所弑。",
 "fig-li-de-2": "",
 "fig-wang-changling-2": "",
 "fig-an-lushan": "发动安史之乱的胡将，身兼三镇节度使拥兵十五万，是唐朝由盛转衰的转折人物。",
 "fig-shi-sim-2": "",
 "fig-yang-guozhong": "唐玄宗时期宰相，与李林甫争权，安禄山以讨伐为名起兵，马嵬驿兵变中被诛。",
 "fig-yang-guifei-2": "",
 "fig-jianzhen": "唐代高僧，六次东渡日本传戒律，双目失明仍不改初志，被尊为日本律宗初祖。",
 "fig-xuanzang": "唐代高僧，孤身西行十七年求法取经，前后译经七十五部，被后世尊为译经之祖。",
 "fig-du-fu": "唐代现实主义的诗圣，一生漂泊困顿而以诗记录时代乱离，其诗因而被称为诗史。",
 "fig-li-bai": "唐代最杰出的诗人，被誉为诗仙，想象奇崛气象万千，作品纵横飘逸善用夸张与神话。",
 "fig-wu-zetian": "中国历史上唯一的女皇帝，扩科举、开殿试，用人唯才，使社会经济在其统治下发展。",
 "fig-dai-rene": "武则天时期名臣，以举贤任能与敢直谏著称，是武周酷吏政治转向清明的关键人物。",
 "fig-li-shimin": "唐太宗，秦王李世民，灭隋定唐的开国之主，以贞观之治与纳谏从谏成为后世典范。",
 "fig-li-shangyin": "唐初名将，凌烟阁二十四功臣之一，随太宗灭诸割据势力，征高句丽而名震天下。",
 "fig-qi": "禹之子，承禹位而废禅让行世袭，启与有扈氏战于甘而取胜，王位世袭自此确立。",
 "fig-taikang": "夏启之子，迷恋田猎而不理政事终至失国，被后羿拒于太石，夏室统治一度中绝。",
 "fig-houyi": "有穷氏首领，夏代著名的射手，传说射落九日，因夏民不服夏氏而取代太康据有穷氏之位。",
 "fig-liu-kang": "太康之子，收拾旧部收复失地，史称少康中兴，是后世论君主德行与国家恢复的典范。",
}

LATIN_FIX = [
 ('讲究oyle 线的转折', '讲究线条的转折'),
]


def patch(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    for fid, news in SUM.items():
        if not news:
            continue
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"summary": "[^"\n]*"', s[m.end():])
        if not m2:
            continue
        a = m.end() + m2.start()
        b = m.end() + m2.end()
        s = s[:a] + '"summary": "%s"' % news + s[b:]
    for a, b in LATIN_FIX:
        s = s.replace(a, b)
    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    if patch(p):
        print('patched', fn)
    compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
print('done')
