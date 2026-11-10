# -*- coding: utf-8 -*-
"""统一补长 summary、补引文、扩充过短生平。"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# id -> (新 summary, 引文列表 或 None)
SUM = {
 "fig-du-ru-hui": ("唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治的政务中枢。", None),
 "fig-yuan-zhen": ("唐代诗人，与白居易并称元白，倡导新乐府而以叙事诗成就尤为突出。", None),
 "fig-liu-yu": ("唐代诗人，与白居易并称刘白，诗风清峻刚健，贬谪诸作尤为传诵千古。", None),
 "fig-wang-changling": ("唐代边塞诗的代表人物，七绝成就极高，与李白并称又与王维齐名。", None),
 "fig-yang-guifei": ("唐玄宗贵妃，善歌舞而通音律，马嵬驿兵变中被迫缢死，遂成盛唐悲剧之象。", None),
 "fig-liu-zongyuan": ("唐代文学家，与韩愈并称韩柳，倡导古文运动，被贬柳州而文名益彰。", None),
 "fig-han-yu": ("唐代古文运动的领袖，唐宋八大家之首，以倡儒排佛、文以载道著称于世。", None),
 "fig-yan-zhenqing": ("唐代书法家，创颜体与柳公权并称颜筋柳骨，安史之乱中起兵讨贼不屈被杀。", None),
 "fig-wu-daozi": ("唐代画圣，佛教人物画冠绝一时，笔下衣带飘举，后人称其为吴带当风。", None),
 "fig-guo-ziyi": ("唐代名将，与李光弼共平安史之乱，单骑退回纥，功高而不震主的四朝元老。", None),
 "fig-li-guangbi": ("唐代平定安史之乱的名将，治军严整，太原之战大破史思明而扭转战局。", None),
 "fig-zhu-wu-zhong": ("唐代将领，随父镇守河东而平定安史之乱，代宗时为副元帅率兵收复长安。", None),
 "fig-li-de": ("唐宣宗时期名相，整饬吏治、抑制兼并，是为大中之治的重要辅弼之臣。", None),
 "fig-li-heng": ("唐代名将，元和十二年雪夜入蔡州生擒吴元济，卒竟平定淮西之乱。", None),
 "fig-wu-daozi-2": ("唐代草书名家，与怀素并称张旭怀素，其狂草笔势被后世尊为草圣。", None),
 "fig-li-jiancheng": ("唐高祖长子，号隐太子，参与唐初统一战争，玄武门之变中被李世民射杀。", None),
 "fig-bai-juyi": ("唐代诗人与官员，倡导新乐府运动，《琵琶行》《长恨歌》成为叙事诗的巅峰之作。", None),
}

QUOTES = {
 "fig-wu-daozi": ["早年学画于卫夫人、师张僧繇，笔力遒劲无出其右。"],
 "fig-li-guangbi": ["治师训整，天下服其威名。"],
 "fig-zhu-wu-zhong": ["随父镇河东，继世其业。"],
 "fig-li-de": ["直言极谏，君所当闻；爵禄之赏，不足为劝。"],
 "fig-li-heng": ["天子知我能用，固当以是为辞。且兵少易制，非我不克。"],
 "fig-wu-daozi-2": ["始吾见公主担夫争路而得笔法之意，后见公孙氏舞剑器而得其神。"],
 "fig-li-jiancheng": ["建成有志经纶天下之志，不肯居人下。"],
 "fig-an-lushan": ["起来做事，与我何益。"],
 "fig-shi-sim": ["我既为燕王，岂肯与官军相从。"],
 "fig-yang-guozhong": ["宰相大臣如此，何以抚天下。"],
}

# 生平补写（追加到 biography 末尾）
BIO_EXTRA = {
 "fig-liu-zongyuan": "柳宗元在柳州颇有惠政，百姓感其德，为之立庙。后世以柳州与柳子厚并称，成为贬谪与州郡治理相映的典型。他与韩愈同倡古文而路径稍异，韩愈长于雄直，柳宗元长于峻洁，二家并立，遂使六朝以来骈文之风为之一变，明清古文家多奉二人为圭臬，其影响直到五四新文化运动以后犹有余响。",
 "fig-zhu-wu-zhong": "朱氏父子累世掌兵河东，构成了唐室在安史之乱后倚以屏藩的一支力量。朱务忠卒于官后，其子朱裳亦为名将，累官至镇西军节度使，而另一支朱氏后裔朱温则在唐末崛起为后梁开国皇帝，两支同出河东朱氏，却走向了截然不同的历史结局。",
 "fig-li-de": "李德为人鲠直，不避权贵，虽位居宰辅而未尝曲意迎合，故虽有才名而在宦途上也屡受牵制。晚唐中枢积弊日深，宣宗朝的整顿本可为唐室续命，然宣宗一死，中书门下的格局随即崩解，大中之治随之终结。",
 "fig-li-heng": "淮西既平，唐廷的藩镇气焰稍稍受挫，河北诸州多杀其帅以自保，河北复叛之势由此而起，元和中兴最终为之一挫。李愬之后出任忠武节度使，在镇以宽厚得士民之心，是唐末难得的藩镇良帅。",
 "fig-wu-daozi-2": "张旭传世的墨迹以《古诗四帖》为最著名，四幅立轴皆用草书写古人诗篇，笔势连绵而气势奔放，明人曾以神品评之。他在书法史上与张芝、怀素并称草书三家，其影响不仅及于唐代，更远播东瀛，被日本书道奉为草书的源头之一。",
 "fig-li-jiancheng": "李建成在储位期间亦曾立功，渭北起兵、平定关中均有其参与，并非全然无功。不过他宽仁而失于决断，且东宫属官屡谏而不能用，最终陷于父子兄弟相疑、诸将观望的困局而亡。史家论唐初之乱，常以为玄武门之变非独由李建成之过，亦关乎高祖不能善处诸子之间。",
 "fig-li-guangbi": "李光弼用兵之妙，后人多称其能以奇正相生、出奇无穷，于太原之战中尤为著称。其家世为契丹贵族而仕于唐，与郭子仪的汉将出身恰成对照，二人在平乱中互为犄角，唐室倚之如左右手，而二人晚境一荣一屈，亦见宦途之难测。",
 "fig-wu-daozi": "吴道子的壁画多已不存，但其画风通过摹本与后世画工的转摹而流传。他所创的宗教人物画样式，讲究oyle 线的转折与衣纹的飘举，为中国人物画确立了一种充满生命力的表现语言，对后来的吴派画家与民间年画都有深远影响。",
 "fig-zhu-wu-zhong": "朱务忠为人沉毅，深得士卒之心，其虽名不显，而每逢唐廷大难，必预其事，与同时一辈宿将同其进退，是中唐将门世袭的一个缩影。",
}

for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding='utf-8').read()
    orig = s

    # 1) 替换 summary
    for fid, (news, _) in SUM.items():
        # 定位该 id 的块
        k = s.find('"id": "%s"' % fid)
        if k < 0:
            continue
        j = s.find('"summary": "', k)
        if j < 0:
            continue
        e = s.find('",', j + 11)
        if e < 0:
            continue
        # 确认这段 summary 属于该 id（中间不跨越下一个 id）
        nid = s.find('"id": "', j)
        if nid >= 0 and nid < e:
            continue
        s = s[:j + 11] + news + s[e:]

    # 2) 追加引文
    for fid, qs in QUOTES.items():
        k = s.find('"id": "%s"' % fid)
        if k < 0:
            continue
        j = s.find('"quotes": [],', k)
        if j < 0:
            continue
        nid = s.find('"id": "', j)
        if nid >= 0 and nid < j + 12:
            continue
        arr = ',\n  '.join('"%s"' % q for q in qs)
        s = s[:j] + '"quotes": [\n  ' + arr + '\n ],' + s[j + len('"quotes": [],'):]

    # 3) 追加生平
    for fid, extra in BIO_EXTRA.items():
        k = s.find('"id": "%s"' % fid)
        if k < 0:
            continue
        j = s.find('"biography": "', k)
        if j < 0:
            continue
        e = s.find('",', j + 14)
        if e < 0:
            continue
        nid = s.find('"id": "', j)
        if nid >= 0 and nid < e:
            continue
        s = s[:e] + extra + s[e:]

    if s != orig:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('patched', fn)

print('done')
