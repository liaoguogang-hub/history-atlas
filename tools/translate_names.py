import io
import json
import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 完整的英美人名音译表。
# 键为 id 中的名字部分（连字符分隔后的小写形式），
# 值为中译名。带前缀的复合名（如 john-wycliffe）优先整体匹配。
NAMES = {
    # ---- 古代近东 / 埃及 / 印度 ----
    "mahinda": "摩诃底那", "pan-geng": "盘庚", "king-zhou-gong": "周公旦",
    "jiang-ziya": "管仲", "king-wu": "周武王", "zhang-dai": "张骞",
    "han-mingdi": "汉明帝", "dong-zhuo": "董卓", "sun-quan": "孙权",
    "taizu-w": "吴太祖", "guo-subai": "郭子白", "li-shouyuan": "李守元",
    "po": "婆罗门", "gao-lianzhi": "高镰之", "sen-zhao": "森昭",
    "shi-simiao": "释思摩", "tangut": "党项人", "shen-kuo": "沈括",
    "zhu-pei": "朱珮", "huang-chong": "黄冲", "huizong": "宋徽宗赵佶",
    "li-zong": "李宗", "wang-zhe": "王哲", "zhang-ju": "张琚",
    "yongle-emperor": "明成祖朱棣", "wanli-emperor": "明神宗朱翊钧",
    "dorgon": "多尔衮", "zheng-chenggong": "郑成功", "tan-sitong": "谭嗣同",
    "li-dazhao": "李大钊", "dong-biwu": "董必武", "zhu-de": "朱德",
    "chen-yun": "陈云", "zhao-ziyang": "赵紫阳", "han-huandi": "汉桓帝",
    "pliny-elder": "老普林尼", "musa-kashuari": "穆萨·卡舒阿里",
    "hao-dong": "郝洞", "gutenberg": "约翰内斯·古腾堡",
    "martin-luther": "马丁·路德", "genghis-khan": "成吉思汗",
    "boccaccio": "薄伽丘", "christopher-columbus": "克里斯托弗·哥伦布",
    "moctezuma": "蒙特祖马二世", "ferdinand-magellan": "费迪南德·麦哲伦",
    "juan-sebastian-elcano": "胡安·塞巴斯蒂安·埃尔卡诺",
    "vasco-da-gama": "瓦斯科·达·伽马",
    "alfonso-de-albuquerque": "阿方索·德·阿尔伯克基",
    "hulagu": "旭烈兀", "rashid-al-din": "拉希德·丁", "alfonso-x": "阿方索十世",
    "rubruck": "鲁布鲁克", "mehmed-ii": "穆罕默德二世",
    "mohammed-ii": "穆罕默德二世", "urban": "于尔班",
    "shangyang": "商鞅", "pierre-bayle": "皮埃尔·培尔",
    "shanfei-kangxi": "顺治与康熙", "matteo-ricci": "利玛窦",
    "johann-adam-schell-von-bell": "汤若望", "francis-xavier": "方济各·沙勿略",
    "songtsen-gampo": "松赞干布", "timur": "帖木儿", "leibniz": "莱布尼茨",
    "meiji-emperor": "明治天皇", "ito-hirobumi": "伊藤博文",
    "yamagata": "山县有朋", "lord-ripon": "里彭伯爵",
    "jamsetji-tata": "贾姆塞吉·塔塔", "otto-von-bismarck": "奥托·冯·俾斯麦",
    "leopold-ii": "利奥波德二世", "cecil-rhodes": "塞西尔·罗兹",
    "william-wilberforce": "威廉·威伯福斯", "abraham-lincoln": "亚伯拉罕·林肯",
    "james-townes": "詹姆斯·汤斯", "henry-cole": "亨利·科尔",
    "victoria": "维多利亚", "cyrus-west-field": "赛勒斯·韦斯特·菲尔德",
    "john-pender": "约翰·潘德", "lenin": "列宁", "stalin": "斯大林",
    "ho-chi-minh": "胡志明", "mahatma-gandhi": "甘地",
    "jawaharlal-nehru": "贾瓦哈拉尔·尼赫鲁", "jl-ramprasad": "贾姆拉·拉姆普拉萨德",
    "john-maynard-keynes": "约翰·梅纳德·凯恩斯", "harry-white": "哈里·怀特",
    "nkrumah": "恩克鲁玛", "leopold-segar-thomas": "利奥波德·西加尔·托马斯",
    "julius-nyerere": "朱利叶斯·尼雷尔", "tito": "铁托", "nehru": "尼赫鲁",
    "mansour-mochtar": "曼苏尔·穆赫塔尔", "neil-armstrong": "尼尔·阿姆斯特朗",
    "yuri-gagarin": "尤里·加加林", "john-f-kennedy": "约翰·肯尼迪",
    "jfk": "肯尼迪", "george-marshall": "乔治·马歇尔", "harry-truman": "哈里·杜鲁门",
    "paul-henri-spaak": "保罗·亨利·斯巴克", "de-gaulle": "戴高乐",
    "khrushchev": "赫鲁晓夫", "castro": "卡斯特罗", "fidel-castro": "菲德尔·卡斯特罗",
    "buzz-aldrin": "巴兹·奥尔德林", "michael-collins": "迈克尔·柯林斯",
    "james-watson": "詹姆斯·沃森", "francis-crick": "弗朗西斯·克里克",
    "rosalind-franklin": "罗莎琳德·富兰克林", "linus-pauling": "莱纳斯·鲍林",
    "inesita-akuntsu": "伊内塞塔·阿孔楚", "mad-cow": "牛瘟",
    "john-von-neumann": "约翰·冯·诺依曼", "claude-shannon": "克劳德·香农",
    "norbert-wiener": "诺伯特·维纳", "diderot": "狄德罗", "voltaire": "伏尔泰",
    "rousseau": "卢梭", "montesquieu": "孟德斯鸠", "immanuel-kant": "康德",
    "angela-merkel": "安格拉·默克尔", "wangari-maathai": "旺加里·马塔伊",
    "gore": "戈尔", "secopia": "塞科皮亚", "yo-yo-ma": "马友友",
    "shirley-chisholm": "雪莉·奇斯霍姆", "richard-nixon": "理查德·尼克松",
    "henry-kissinger": "亨利·基辛格", "salvador-allende": "萨尔瓦多·阿连德",
    "gamal-abdel-nasser": "加马尔·阿卜杜勒·纳赛尔",
    "john-foster-dulles": "约翰·福斯特·杜勒斯", "suharto": "苏哈托",
    "nguyen-van-thieu": "阮文绍", "pierre-de-coubertin": "皮埃尔·德·顾拜旦",
    "juan-antonio-samaranch": "胡安·安东尼奥·萨马兰奇",
    "eduard-said": "爱德华·萨义德", "luis-angeles-jimenez": "路易斯·安赫莱斯·希门尼斯",
    "cosimo-de-medici": "科西莫·德·美第奇", "lorenzo-de-medici": "洛伦佐·德·美第奇",
    "cyril-and-methodius": "西里尔与美多丢", "erik-the-red": "红发埃里克",
    "leif-erikson": "莱夫·埃里克松", "suleiman-the-magnificent": "苏莱曼大帝",
    "king-ashoka": "阿育王", "james-cook": "詹姆斯·库克", "te-piki": "特·皮基",
    "wang-xuance": "王玄策", "leonidas": "列奥尼达", "modu-chanyu": "冒顿单于",
    "robert-hart": "罗伯特·哈特", "edward-iii": "爱德华三世",
    "henry-v": "亨利五世", "joan-of-arc": "圣女贞德", "ismail-isi": "伊斯梅尔·伊斯",
    "shah-isfandiyar": "伊斯凡迪亚尔沙", "john-wycliffe": "约翰·威克里夫",
    "john-wesley": "约翰·卫斯理", "ibn-majid": "伊本·马吉德",
    "ahmad-ibn-majid": "艾哈迈德·伊本·马吉德", "yi-shi-xin": "伊士欣",
    "shanfu": "商鞅", "geoffrey-hinton": "杰弗里·辛顿",
    "yann-lecun": "杨立昆", "yoshua-bengio": "约书亚·本吉奥",
    "charles-ellington": "查尔斯·惠灵顿",
    "liu Bowen": "刘昫", "li Yuan": "李元", "huizong2": "宋徽宗",
    "tan-si-tong": "谭嗣同", "qin-hui": "秦桧", "han-zheng": "韩正",
    "shan-han": "单桓", "yu-wen-shu": "虞世南", "yang-yang": "杨炀",
    "zhou-bo": "周勃", "han-xin": "韩信", "han-zhaodi": "汉昭帝",
    "kublai": "忽必烈",
}

# 通用音译：用于表外的名字
TRANS = {
    "john": "约翰", "james": "詹姆斯", "peter": "彼得", "paul": "保罗",
    "george": "乔治", "charles": "查尔斯", "william": "威廉", "henry": "亨利",
    "edward": "爱德华", "richard": "理查德", "robert": "罗伯特", "david": "戴维",
    "thomas": "托马斯", "arthur": "亚瑟", "alfred": "阿尔弗雷德", "edmund": "埃德蒙",
    "harold": "哈罗德", "gustav": "古斯塔夫", "frederick": "弗雷德里克",
    "ferdinand": "斐迪南", "philip": "菲利普", "louis": "路易", "napoleon": "拿破仑",
    "alexander": "亚历山大", "constantine": "君士坦丁", "julius": "朱利叶斯",
    "caesar": "凯撒", "claudius": "克劳狄乌斯", "nero": "尼禄", "augustus": "奥古斯都",
    "tiberius": "提比略", "domitian": "图密善", "trajan": "图拉真", "hadrian": "哈德良",
    "marcus": "马库斯", "sulla": "苏拉", "pompey": "庞培", "mary": "玛丽",
    "elizabeth": "伊丽莎白", "victoria": "维多利亚", "edith": "伊迪丝",
    "cecilia": "塞西莉亚", "agnes": "艾格尼丝", "helen": "海伦",
    "isabella": "伊莎贝拉", "joan": "琼", "marie": "玛丽", "catherine": "凯瑟琳",
    "anne": "安妮", "caroline": "卡罗琳", "louise": "路易丝", "margaret": "玛格丽特",
    "sophia": "索菲娅", "julia": "茱莉亚", "emily": "埃米莉", "alice": "爱丽丝",
    "dorothy": "多萝西", "frances": "弗朗西丝", "michael": "迈克尔",
    "robert2": "罗贝尔", "william2": "纪尧姆", "richard2": "理查", "henry2": "亨利",
    "charles2": "夏尔", "louis2": "路易", "john2": "让", "pierre": "皮埃尔",
    "andre": "安德烈", "antoine": "安托万", "claude": "克洛德", "francois": "弗朗索瓦",
    "jules": "朱尔", "marcel": "马塞尔", "gustave": "古斯塔夫", "auguste": "奥古斯特",
    "nicolas": "尼古拉", "benedict": "本笃", "romeo": "罗密欧",
    "william3": "威廉", "henry3": "亨利", "charles3": "夏尔", "maria": "玛丽亚",
    "john3": "约翰", "louis3": "路易", "stephen": "斯蒂芬", "thomas2": "托马索",
    "nicola": "尼科拉", "giuseppe": "朱塞佩", "francesco": "弗朗切斯科",
    "michelangelo": "米开朗基罗", "leonardo": "列奥纳多", "raphael": "拉斐尔",
    "donatello": "多纳泰罗", "titian": "提香", "rembrandt": "伦勃朗",
    "goya": "戈雅", "monet": "莫奈", "van": "梵", "dali": "达利", "picasso": "毕加索",
    "matisse": "马蒂斯", "kandinsky": "康定斯基", "gutenberg": "古腾堡",
    "copernicus": "哥白尼", "kepler": "开普勒", "galileo": "伽利略",
    "newton": "牛顿", "einstein": "爱因斯坦", "bohr": "玻尔", "curie": "居里",
    "darwin": "达尔文", "linnaeus": "林奈", "lavoisier": "拉瓦锡",
    "pasteur": "巴斯德", "koch": "科赫", "freud": "弗洛伊德", "jung": "荣格",
    "nietzsche": "尼采", "marx": "马克思", "engels": "恩格斯",
    "confucius": "孔子", "mencius": "孟子", "laozi": "老子", "zhuangzi": "庄子",
    "sima": "司马", "ban": "班", "xunzi": "荀子", "hanfeizi": "韩非子",
    "shang": "商", "zhou": "周", "qin": "秦", "han": "汉", "tang": "唐",
    "song": "宋", "yuan": "元", "ming": "明", "sui": "隋",
    "king": "国王", "queen": "女王", "emperor": "皇帝", "empress": "皇后",
    "prince": "王子", "duke": "公爵", "saint": "圣", "pope": "教皇",
    "caliph": "哈里发", "sultan": "苏丹", "shah": "沙", "khan": "汗",
    "tsar": "沙皇", "general": "将军", "admiral": "海军上将", "president": "总统",
    "minister": "大臣", "senator": "元老", "governor": "总督",
    "darwin2": "达尔文", "socrates": "苏格拉底", "plato": "柏拉图",
    "aristotle": "亚里士多德", "buddha": "释迦牟尼", "akbar": "阿克巴",
    "kautilya": "考底利耶", "nagarjuna": "龙树", "sankara": "商羯罗",
    "hypatia": "希帕提娅", "ashoka": "阿育王", "hammurabi": "汉谟拉比",
    "sargon": "萨尔贡", "nebuchadnezzar": "尼布甲尼撒", "cyrus": "居鲁士",
    "darius": "大流士", "xerxes": "薛西斯", "julius": "朱利叶斯",
    "marco": "马可", "polo": "波罗", "columbus": "哥伦布", "magellan": "麦哲伦",
    "shakespeare": "莎士比亚", "watt": "瓦特", "lincoln": "林肯",
    "roosevelt": "罗斯福", "churchill": "丘吉尔", "tolstoy": "托尔斯泰",
    "murasaki": "紫式部", "mansa": "曼萨", "musa": "穆萨", "monte": "蒙特",
    "zuma": "祖玛", "pachacuti": "帕查库特克", "marie": "玛丽", "curie": "居里",
    "alan": "艾伦", "turing": "图灵", "yuan": "元", "longping": "隆平",
    "tu": "屠", "youyou": "呦呦", "nash": "纳什", "tupac": "图帕克",
    "amaru": "阿马鲁", "magsaysay": "麦格赛赛", "savonarola": "萨沃纳罗拉",
    "ramon": "拉蒙", "lopez": "洛佩斯", "pilar": "皮拉尔",
}

# 常见的「姓-名」结构：中文里姓在前名在后
KNOWN_SURNAME_FIRST = True


def translate(slug):
    s = slug.replace("_", "-").strip("-")
    if not s:
        return None
    if s.lower() in NAMES:
        return NAMES[s.lower()]
    parts = [p for p in s.split("-") if p]
    out = []
    for p in parts:
        key = p.lower()
        if key in TRANS:
            out.append(TRANS[key])
        elif key in NAMES:
            out.append(NAMES[key])
        else:
            out.append(None)
    if any(o is None for o in out):
        # 有未识别段，回退为「音译+原文」
        trans = []
        for p in parts:
            key = p.lower()
            if key in TRANS:
                trans.append(TRANS[key])
            else:
                trans.append(p.capitalize())
        return "·".join(trans)
    return "".join(out)


CJK = re.compile(r"[\u4e00-\u9fff]")


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    named = 0
    kept = 0
    left = []
    for f in data.get("figures") or []:
        if "待补充条目" not in (f.get("biography") or ""):
            continue
        # 名字已经是中文时不得改写。
        # 早期版本只要发现占位传记就按 id 音译覆盖 name，
        # 把「司马懿」「廉颇」这类本身正确的名字改成了「司马·Yi」。
        if CJK.search(f.get("name") or ""):
            kept += 1
            continue
        slug = f["id"][4:] if f["id"].startswith("fig-") else f["id"]
        cn = translate(slug)
        if cn:
            f["name"] = cn
            f["role"] = "历史人物"
            f["summary"] = f"{cn}是这一时期的相关人物，其事迹见于此一时期的史籍记载。"
            f["biography"] = (
                f"{cn}是相关时期的重要人物，其生平与当时的社会变动紧密相系，"
                f"相关事迹见史籍记载。此条为待补充条目，后续将补齐详细生平与事迹。"
            )
            named += 1
        else:
            left.append(f["id"])

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: translated {named} placeholder names, "
          f"kept {kept} chinese names, {len(left)} left")
    if left:
        print("  remaining:", left[:40])


if __name__ == "__main__":
    main()
