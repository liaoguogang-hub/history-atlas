# -*- coding: utf-8 -*-
"""用正则安全地替换 summary / quotes / 追加 biography。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

SUM = {
 "fig-du-ru-hui": "唐初名相，长于决断，与房玄龄并称房谋杜断，是贞观之治的政务中枢所在。",
 "fig-yuan-zhen": "唐代诗人，与白居易并称元白，倡导新乐府而以叙事诗成就尤为突出者。",
 "fig-liu-yu": "唐代诗人，与白居易并称刘白，诗风清峻刚健，贬谪诸作尤为传诵千古。",
 "fig-wang-changling": "唐代边塞诗的代表人物，七绝成就极高，与李白并称又与王维齐名。",
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

BIO_EXTRA = {
 "fig-liu-zongyuan": "柳宗元在柳州颇有惠政，百姓感其德，为之立庙。后世以柳州与柳子厚并称，成为贬谪与州郡治理相映的典型。他与韩愈同倡古文而路径稍异，韩愈长于雄直，柳宗元长于峻洁，二家并立，遂使六朝以来骈文之风为之一变，明清古文家多奉二人为圭臬，其影响直到新文化运动以后犹有余响。",
 "fig-zhu-wu-zhong": "朱氏父子累世掌兵河东，构成了唐室在安史之乱后倚以屏藩的一支力量。朱务忠卒于官后，其子朱裳亦为名将，累官至镇西军节度使，而另一支同出河东朱氏的朱温，则在唐末崛起为后梁开国皇帝，两支同宗却走向了截然不同的历史结局。",
 "fig-li-de": "李德为人鲠直，不避权贵，虽位居宰辅而未尝曲意迎合，故虽有才名而在宦途上也屡受牵制。晚唐中枢积弊日深，宣宗朝的整顿本可为唐室续命，然宣宗一死，中书门下的格局随即崩解，大中之治随之终结。",
 "fig-li-heng": "淮西既平，唐廷的藩镇气焰稍稍受挫，河北诸州多杀其帅以自保，河北复叛之势由此而起，元和中兴最终为之一挫。李愬之后出任忠武节度使，在镇以宽厚得士民之心，是唐末难得的藩镇良帅。",
 "fig-wu-daozi-2": "张旭传世的墨迹以《古诗四帖》为最著名，四幅立轴皆用草书写古人诗篇，笔势连绵而气势奔放，明人曾以神品评之。他在书法史上与张芝、怀素并称草书三家，其影响不仅及于唐代，更远播东瀛，被日本书道奉为草书的源头之一。",
 "fig-li-jiancheng": "李建成在储位期间亦曾立功，渭北起兵、平定关中均有其参与，并非全然无功。不过他宽仁而失于决断，且东宫属官屡谏而不能用，最终陷于父子兄弟相疑、诸将观望的困局而亡。史家论唐初之乱，常以为玄武门之变非独由李建成之过，亦关乎高祖不能善处诸子之间。",
 "fig-li-guangbi": "李光弼用兵之妙，后人多称其能以奇正相生、出奇无穷，于太原之战中尤为著称。其家世为契丹贵族而仕于唐，与郭子仪的汉将出身恰成对照，二人在平乱中互为犄角，唐室倚之如左右手，而二人晚境一荣一屈，亦见宦途之难测。",
 "fig-wu-daozi": "吴道子的壁画多已不存，但其画风通过摹本与后世画工的转摹而流传。他所创的宗教人物画样式，讲究线条的转折与衣纹的飘举，为中国人物画确立了一种充满生命力的表现语言，对后来的吴派画家与民间年画都有深远影响。",
 "fig-yang-guozhong": "杨国忠在任内排斥异己，把持朝政，其子杨暄亦居显位，进一步加深了唐廷内部的派系之争。他对安禄山既倚为爪牙又处处牵制，终于把边镇逼到不得不反的地步，这一过程正体现中唐藩镇体制下中央与地方的深刻矛盾。",
 "fig-an-lushan": "安禄山起兵之后，唐廷的应对颇见仓促，潼关失守、玄宗西幸、马嵬兵变接踵而至，倉卒之间往往仓卒决断，暴露出盛世之下政治机器的僵化。他本人后来虽死于内部争斗，其乱所开启的藩镇时代却延续了两百余年。",
 "fig-shi-sim": "史思明与安庆绪、安禄山父子同类的相残，反映出叛军集团内部缺乏稳固的统属关系，只能以实力相争。这正是唐末藩镇与叛军普遍的政治特征，也是这一时期历史人物多为武人而非士人的根本原因。",
 "fig-yang-guifei": "后世对杨玉环的评说历经变化，从唐宋时期她被斥为祸水，到明清文人同情其身世，再到近人从制度与权力运作的角度重新审视这段历史，她始终是理解盛唐政治与宫廷生活的一个关键切面。",
 "fig-han-yu": "韩愈在潮州任上虽仅八个月，却以驱鳄、赈贫、兴学诸事深得民心，其离任时州人送者皆号泣，潮人至今称「韩愈刺潮」。他的文章与胆识并重，是唐代士大夫在政治高压下仍敢言说的一种象征。",
 "fig-yan-zhenqing": "颜真卿晚年屡遭贬谪而忧国不改，其《乞御书放生表》《让宪部尚书表》等奏章，措辞恳切，可见其心迹。他死后，李希烈将他的首级示于三日，李白闻之，题诗《哭颜季文》以志哀悼，其人格之重可见一斑。",
 "fig-guo-ziyi": "郭子仪晚年居第宾客之盛为天下第一，其为人温厚，与李光弼虽有隙而终能相安，两将同处一朝而不同器，俱以功成身退见称。唐人形容其处境云「功盖天下而朝不忌，位极人臣而众不嫉」，正是盛唐名将最难得的品格。",
 "fig-li-huaiguang": "",
}


def patch_file(path):
    s = io.open(path, encoding='utf-8').read()
    orig = s

    # --- summary ---
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

    # --- quotes ---
    for fid, qs in QUOTES.items():
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"quotes": \[\]', s[m.end():])
        if not m2:
            continue
        a = m.end() + m2.start()
        b = m.end() + m2.end()
        arr = ',\n  '.join('"%s"' % q for q in qs)
        s = s[:a] + '"quotes": [\n  ' + arr + '\n ]' + s[b:]

    # --- biography 追加 ---
    for fid, extra in BIO_EXTRA.items():
        if not extra:
            continue
        m = re.search(r'"id": "%s"' % re.escape(fid), s)
        if not m:
            continue
        m2 = re.search(r'"biography": "[^"]*"', s[m.end():])
        if not m2:
            continue
        a = m.end() + m2.end() - 1
        s = s[:a] + extra + s[a:]

    if s != orig:
        io.open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sy_b') and f.endswith('.py')):
    p = os.path.join(HERE, fn)
    if patch_file(p):
        print('patched', fn)
    try:
        compile(io.open(p, encoding='utf-8').read(), fn, 'exec')
    except SyntaxError as e:
        print('SYNTAX FAIL', fn, e)
print('done')
