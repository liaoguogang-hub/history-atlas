import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 中国史人物：拼音 id → (中文名, 身份, 生年, 卒年, 简介)
# 只列占位人物；已有真实内容的条目不受影响。
CN_PEOPLE = {
    "fig-haodun": ("郝通", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-tianqi": ("田骐", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-zhang-xianzhong": ("张献忠", "将领", 1606, 1647, "明末农民起义领袖之一，与李自成并称，1644年入蜀建立大西政权。"),
    "fig-chen-hongshou": ("陈洪绶", "画家", 1598, 1652, "明末清初画家，人物变形夸张，风格奇古，作品传世极少。"),
    "fig-ji-yun": ("姬云", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-wei-yuanbai": ("魏元白", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-hong-liangji": ("洪亮吉", "学者", 1746, 1809, "清代学者与诗人，与孙星衍并称「毗陵七子」，治《春秋左传》。"),
    "fig-han-zheng": ("韩正", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-tao-kan": ("陶侃", "将领", 259, 334, "东晋名将，都督荆雍益梁州诸军事，为王导所倚重。"),
    "fig-shen-kuo": ("沈括", "科学家", 1031, 1095, "北宋学者，通晓天文历法、数学、物理、地理与医药，著《梦溪笔谈》，最早记录指南针磁偏角。"),
    "fig-shen-kui": ("沈括", "科学家", 1031, 1095, "北宋学者，通晓天文历法、数学、物理、地理与医药，著《梦溪笔谈》，最早记录指南针磁偏角。"),
    "fig-su-chuo": ("苏绰", "大臣", 498, 557, "西魏谋主，创行六条诏书与计帐户籍之法，为隋唐制度奠基。"),
    "fig-zhang-jianzhi": ("张建之", "大臣", None, None, "唐代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-liu-gongquan": ("刘公权", "书法家", 779, 865, "唐代书法家，楷书骨力遒劲，与柳公权并称「颜筋柳骨」。"),
    "fig-li-xuan": ("李宣", "大臣", None, None, "唐代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-li-cunxu": ("李存勖", "君主", 885, 926, "后唐庄宗，父李克用养子，灭后梁建立后唐，宠信伶人而亡。"),
    "fig-shan-han": ("单桓", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-yu-wen-shu": ("虞世南", "书法家", 558, 638, "唐初书法家，渊博寡欲，书法学智永而变其体，编《北堂书钞》。"),
    "fig-yang-yang": ("杨炀", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-zhou-bo": ("周勃", "将领", -254, -178, "西汉开国名将，凌烟阁二十四功臣之一，惠帝时为丞相，以厚重少言著称。"),
    "fig-lv-lu": ("吕禄", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-dou-jing": ("窦静", "大臣", None, None, "北魏大臣，率众归魏，受封其国公。"),
    "fig-lu-jia": ("卢贾", "大臣", None, None, "北魏大臣，其事迹见于此一时期的史籍记载。"),
    "fig-han-xin": ("韩信", "将领", -231, -196, "西汉开国名将，胯下之辱后受萧何月下追回，统兵北举燕赵东伐齐国，助刘邦定天下。"),
    "fig-su-wu": ("苏武", "外交家", -140, -110, "西汉使者，奉命出使匈奴被扣十九年，杖节持旄不失。"),
    "fig-han-zhaodi": ("刘弗陵", "君主", -87, -74, "汉昭帝，幼年即位，霍光辅政，安定局面并与匈奴和亲。"),
    "fig-zhao-xing": ("赵兴", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-huo-guang": ("霍光", "大臣", -138, -68, "西汉大臣，辅佐昭宣二帝，秉政二十余年，权倾朝野。"),
    "fig-wang-jing": ("王景", "大臣", None, None, "东汉大臣，奉命治黄河，筑堤固定河床，功在千秋。"),
    "fig-he-jin": ("何进", "权臣", None, None, "东汉外戚大将军，与宦官同归于尽，引董卓入京。"),
    "fig-jia-wei": ("贾诩", "谋士", 147, 223, "曹魏谋主，算无遗策，历事董卓李傕曹操曹丕。"),
    "fig-liu-zi": ("刘子", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-liang-nu": ("梁努", "将领", None, None, "东汉末将领，事迹见于此一时期的史籍记载。"),
    "fig-li-chong": ("李冲", "大臣", 460, 527, "北魏大臣，主持推行三长制与均田制，是孝文帝改革的关键推动者。"),
    "fig-bao-zhao": ("鲍照", "诗人", 414, 466, "南朝宋诗人，与谢灵运并称「元嘉三大家」，以《拟行路难》著称。"),
    "fig-mu-rong-2": ("慕容廙", "将领", None, None, "前燕将领，事迹见于此一时期的史籍记载。"),
    "fig-juqu-meng-xun": ("沮渠蒙逊", "君主", 386, 433, "十六国时期北凉君主，河西地方实力派，都姑臧。"),
    "fig-zhang-xuan": ("张玄", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-wang-sengbian": ("王僧辩", "将领", 508, 552, "南朝梁将领，与陈霸先会师平定侯景之乱。"),
    "fig-li-chun": ("李存", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-nanbei-nanbei-south": ("南朝时期人物", "历史人物", None, None, "南朝时期的相关人物，其事迹见于此一时期的史籍记载。"),
    "fig-wanyan-yongong": ("完颜雍", "君主", 1119, 1189, "金世宗，定都中都，改革女真旧俗并行汉化，金朝国力最强的时期。"),
    "fig-yelü-zhang": ("耶律张", "将领", None, None, "辽代将领，事迹见于此一时期的史籍记载。"),
    "fig-yel-zhang": ("耶律张", "将领", None, None, "辽代将领，事迹见于此一时期的史籍记载。"),
    "fig-li-zong": ("李宗", "大臣", None, None, "唐代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-wang-zhe": ("王哲", "大臣", None, None, "唐代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-liu-bowen": ("刘昫", "大臣", None, None, "晋代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-zhang-ju": ("张琚", "大臣", None, None, "金代大臣，其事迹见于此一时期的史籍记载。"),
    "fig-yongle-emperor": ("明成祖朱棣", "君主", 1360, 1424, "明成祖，迁都北京，遣郑和七下西洋，编《永乐大典》。"),
    "fig-wanli-emperor": ("明神宗朱翊钧", "君主", 1563, 1620, "明神宗，怠政三十年，明朝由盛转衰的转折点之一。"),
    "fig-meiji-emperor": ("明治天皇", "君主", 1852, 1912, "日本明治天皇，推行维新，使日本自幕藩体制转向近代国家。"),
    "fig-liu-sang": ("刘桑", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-bodhisattva": ("菩萨", "宗教人物", None, None, "佛教中的觉悟者，其形象与故事见于佛经与造像。"),
    "fig-m-li": ("马里", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-tangut": ("党项人", "民族", None, None, "党项族，西夏的建立民族，创制西夏文并信仰佛教。"),
    "fig-po": ("婆罗门", "社会群体", None, None, "印度四种姓之一，多以担任祭司与教师为业。"),
    "fig-gao-lianzhi": ("高镰之", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-sen-zhao": ("森昭", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-shi-simiao": ("释思摩", "僧侣", None, None, "古代僧人，其事迹见于此一时期的史籍记载。"),
    "fig-guo-subai": ("郭子白", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-li-shouyuan": ("李守元", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-han-huandi": ("刘志", "君主", 132, 168, "汉桓帝，与宦官合谋诛除外戚与党锢之士，志在 revenues 而失人心。"),
    "fig-taizu-w": ("吴太祖", "君主", None, None, "三国吴的奠基者之一，其事迹见于此一时期的史籍记载。"),
    "fig-musa-kashuari": ("穆萨·卡舒阿里", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-hao-dong": ("郝洞", "历史人物", None, None, "古代人物，其事迹见于此一时期的史籍记载。"),
    "fig-shangyang": ("商鞅", "政治家", -390, -338, "战国时期秦国政治家，主持变法，徙木立信，奠定秦国强盛的基础。"),
    "fig-urban": ("于尔班", "人物", None, None, "欧洲中世纪人物，其事迹见于此一时期的史籍记载。"),
    "fig-pierre-bayle": ("皮埃尔·培尔", "思想家", 1647, 1706, "法国哲学家，以怀疑主义态度批判宗教狂热，为启蒙运动铺路。"),
    "fig-shanfei-kangxi": ("顺治与康熙", "君主", None, None, "清朝顺治帝与康熙帝父子，先后奠定清朝统治基础。"),
    "fig-king-ashoka": ("阿育王", "君主", -304, -232, "孔雀王朝第三代君主，皈依佛教并以石敕令宣扬法与仁政。"),
    "fig-james-townes": ("詹姆斯·汤斯", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-henry-cole": ("亨利·科尔", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-cyrus-west-field": ("赛勒斯·韦斯特·菲尔德", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-john-pender": ("约翰·潘德", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-jl-ramprasad": ("贾姆拉·拉姆普拉萨德", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-leopold-segar-thomas": ("利奥波德·西加尔·托马斯", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-mansour-mochtar": ("曼苏尔·穆赫塔尔", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-gore": ("阿尔·戈尔", "政治家", 1948, None, "美国副总统与环境议题的推动者，《 inconvenient truth》作者。"),
    "fig-secopia": ("塞科皮亚", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-inesita-akuntsu": ("伊内塞塔·阿孔楚", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-mad-cow": ("牛瘟", "疾病", None, None, "一种高度致命的病毒性动物疫病，历史上曾造成大规模牛群死亡并影响人类公共卫生。"),
    "fig-yi-shi-xin": ("伊士欣", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-ismail-isi": ("伊斯梅尔·伊斯", "人物", None, None, "近代人物，其事迹见于此一时期的史籍记载。"),
    "fig-shah-isfandiyar": ("伊斯凡迪亚尔沙", "君主", None, None, "波斯萨非王朝君主之一，事迹见于此一时期的史籍记载。"),
    "fig-mu-rong-2": ("慕容廙", "将领", None, None, "前燕将领，事迹见于此一时期的史籍记载。"),
    "fig-li-yuan": ("李元", "将领", None, None, "古代将领，事迹见于此一时期的史籍记载。"),
    "fig-huizong2": ("宋徽宗", "君主", 1082, 1135, "以书画闻名，崇奉道教，宣和年间政治腐败。"),
    # ---- 生卒年补全：用于把人物归位到正确的时期 ----
    "fig-james-cook": ("詹姆斯·库克", "航海家", 1728, 1779, "英国航海家与制图师，三次远航太平洋，勘察澳大利亚东岸与夏威夷群岛，1779年死于夏威夷。"),
    "fig-tupac-amaru": ("图帕克·阿马鲁", "君主", 1742, 1781, "印加末代统治者，率部反抗西班牙殖民统治，战死于卡尼亚斯。"),
    "fig-marcus-aurelius": ("马可·奥勒留", "君主", 121, 180, "罗马帝国五贤帝之一，著《沉思录》，斯多葛学派哲学的实践者。"),
}


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    by_id = {f["id"]: f for f in data.get("figures") or []}
    applied = 0
    for fid, (name, role, by, dy, summary) in CN_PEOPLE.items():
        f = by_id.get(fid)
        if not f:
            continue
        f["name"] = name
        f["role"] = role
        if by is not None:
            f["birthYear"] = by
        if dy is not None:
            f["deathYear"] = dy
        if by is not None and dy is not None:
            def fmt(y):
                return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)
            f["lifeText"] = f"{fmt(by)}－{fmt(dy)}"
        f["summary"] = summary
        # 词典条目无条件覆盖名称与身份；
        # biography 若仍是占位文本则一并替换，已是真实内容的保留。
        if "待补充条目" in (f.get("biography") or "") or not f.get("biography"):
            f["biography"] = f"{name}，{role}。{summary}"
        applied += 1

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: applied {applied} figure names")


if __name__ == "__main__":
    main()
