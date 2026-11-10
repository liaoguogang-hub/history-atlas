import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 事件 id → 中文名（精确映射）
EVENT_NAMES = {
    # ---- 宋 ----
    "ev-song-shaoxing-treaty": "绍兴和议",
    "ev-song-wen-tianxiang": "文天祥抗元",
    "ev-song-jin-rise": "金朝崛起",
    "ev-song-jin-shijin": "金室建国",
    "ev-song-kaixi": "宋夏和议",
    "ev-song-yuefei": "岳飞抗金",
    "ev-song-yuangong": "元军攻宋",
    "ev-song-caizhou": "蔡州之战",
    "ev-song-cup-wine": "杯酒释兵权",
    "ev-song-qingliang": "庆历新政",
    "ev-song-wanganshi": "王安石变法",
    "ev-song-xining": "西夏建国",
    "ev-song-yuanyou": "元祐更化",
    "ev-song-nansong": "南宋建立",
    "ev-song-jingkang": "靖康之变",
    "ev-song-liao-chanyuan": "澶渊之盟",
    "ev-song-yashan": "崖山海战",
    "ev-song-wanyan": "宋金和议",
    "ev-song-jin": "金朝建立",
    "ev-song-liao": "辽朝建立",
    "ev-song-yuan": "元灭南宋",
    "ev-song-founding": "北宋建立",
    "ev-song-ne": "北宋灭亡",

    # ---- 辽 ----
    "ev-liao-shengzong": "辽圣宗时期澶渊之盟",

    # ---- 元 ----
    "ev-yuan-jasaga": "札剌合台西征",
    "ev-yuan-xiya": "西夏的兴衰",
    "ev-yuan-xixia": "西夏与宋辽的三角",
    "ev-yuan-ailiboge": "爱理戠西征",
    "ev-yuan-kublai": "忽必烈建元与统一",
    "ev-yuan-hailing": "金海陵南侵",
    "ev-yuan-founding": "元朝建立",
    "ev-yuan-xing-sheng": "行省制度确立",
    "ev-yuan-dadu": "元大都建成",
    "ev-yuan-miao": "元大都规划营建",
    "ev-yuan-fall": "元朝灭亡",
    "ev-yuan-mongol-unify": "蒙古统一中国",

    # ---- 明 ----
    "ev-ming-hongwu": "洪武之治",
    "ev-ming-zhenghe": "郑和下西洋",
    "ev-ming-tumu": "土木堡之变",
    "ev-ming-yu-qian": "于谦保卫北京",
    "ev-ming-hongzhi": "弘治中兴",
    "ev-ming-jiajing": "嘉靖朝",
    "ev-ming-qi-jiguang": "戚继光抗倭",
    "ev-ming-longqing": "隆庆和议与开关",
    "ev-ming-wanli": "万历朝",
    "ev-ming-hai-ru": "海瑞整饬吏治",
    "ev-ming-xu-xiake": "徐霞客游记",
    "ev-ming-tianqi": "天启朝",
    "ev-ming-chongzhen": "崇祯朝",
    "ev-ming-liaodong": "辽东战事",
    "ev-ming-buzhou": "九边军事部署",
    "ev-ming-lizicheng": "李成梁戍边",
    "ev-ming-wangyangming": "王阳明心学",
    "ev-ming-founding": "明朝建立",
    "ev-ming-yongle": "永乐盛世",
    "ev-ming-sea": "郑和下西洋",
    "ev-ming-yitiaobian": "土木堡之变",
    "ev-ming-fall": "明朝灭亡",
    "ev-ming-qing": "明清易代",
    "ev-ming-chengzu": "永乐迁都北京",
    "ev-ming-one-tax": "一条鞭法推行",
    "ev-ming-jishitai": "军机处设立",
    "ev-ming-lizhi": "李贽反叛",

    # ---- 清 ----
    "ev-qing-qing-enter": "清军入关",
    "ev-qing-tifa": "剃发易服",
    "ev-qing-yaksa": "雅克萨之战",
    "ev-qing-junji": "八旗与绿营",
    "ev-qing-siku": "编纂《四库全书》",
    "ev-qing-wenziyu": "文字狱",
    "ev-qing-bailianjiao": "白莲教起义",
    "ev-qing-jiaqing": "嘉庆朝",
    "ev-qing-guangzhou-trade": "广州一口通商",
    "ev-qing-nanjing-treaty": "《南京条约》签订",
    "ev-qing-jiawu": "甲午战争",
    "ev-qing-wuxu": "戊戌变法",
    "ev-qing-new-policies": "清末新政",
    "ev-qing-kangxi": "康熙盛世",
    "ev-qing-yongzheng": "雍正改革",
    "ev-qing-qianlong": "康乾盛世",
    "ev-qing-founding": "清朝建立",
    "ev-qing-opium-war": "鸦片战争",
    "ev-qing-taiping": "太平天国运动",
    "ev-qing-yangwu": "洋务运动",
    "ev-qing-xinhai": "辛亥革命",
    "ev-qing-self-strengthen": "自强运动",
    "ev-qing-hundred-days": "戊戌变法",
    "ev-qing-mulan": "木兰围场秋狝",
    "ev-qing-sanfan": "三藩之乱",
    "ev-qing-taiwan": "统一台湾",
    "ev-qing-wuwu": "十全武功",

    # ---- 近代 ----
    "ev-modern-provisional": "南京临时政府成立",
    "ev-modern-yuan-shikai": "袁世凯窃取革命果实",
    "ev-modern-empire": "洪宪帝制",
    "ev-modern-republic": "中华民国建立",
    "ev-modern-may-fourth": "五四运动",
    "ev-modern-communist-party": "中国共产党成立",
    "ev-modern-japanese-aggression": "九一八事变",
    "ev-modern-japanese": "甲午战争",
    "ev-modern-victory": "抗日战争胜利",
    "ev-modern-liberation": "解放战争胜利",

    # ---- 新中国 ----
    "ev-prc-beidou": "北斗卫星导航系统组网",
    "ev-prc-new-era": "新时代开启",
    "ev-prc-belt-road": "一带一路倡议提出",
    "ev-prc-reform": "改革开放",
    "ev-prc-founding": "中华人民共和国成立",
    "ev-prc-first-five-year": "第一个五年计划",
    "ev-prc-two-bombs": "两弹一星工程",
    "ev-prc-special-zones": "经济特区建立",
    "ev-prc-hong-kong": "香港回归祖国",
    "ev-prc-macao": "澳门回归祖国",
    "ev-prc-wto": "加入世界贸易组织",
    "ev-prc-olympic": "北京奥运会",
    "ev-prc-wenchange": "文化大革命",
    "ev-prc-reformopen": "农村与城市经济体制改革",
    "ev-prc-scitech": "科技与教育振兴",
    "ev-prc-hu": "载人航天工程",
    "ev-prc-supercomputer": "超级计算机研制",
    "ev-prc-genome": "人类基因组计划参与",
    "ev-prc-pandemic": "抗击新冠疫情",
    "ev-prc-poverty": "脱贫攻坚",

    # ---- 唐 ----
    "ev-tang-hezhong": "安史之乱中的河中之变",
    "ev-tang-gaozu": "唐朝建立",
    "ev-tang-kaixuan": "开元盛世",
    "ev-tang-wuzhou": "武周建立",
    "ev-tang-anlushan": "安史之乱",
    "ev-tang-poetry": "唐诗兴盛",
    "ev-tang-xuanzang": "玄奘西行",
    "ev-tang-jianzhen": "鉴真东渡",
    "ev-tang-luoyang-fall": "安史之乱平定",
    "ev-tang-xuanwumen": "玄武门之变",

    # ---- 魏晋南北朝 ----
    "ev-weijin-nanyue": "衣冠南渡与南朝建立",
    "ev-weijin-taikang": "太康之治",
    "ev-weijin-feishui": "淝水之战",
    "ev-weijin-yongjia": "永嘉之乱",
    "ev-nanbei-nanbei-south": "南朝兴替",
    "ev-nanbei-xiaowen": "孝文帝改革",
    "ev-nanbei-kaifeng": "北魏统一北方",
    "ev-sixteen-kingdoms": "十六国时期",
    "ev-three-wei-ding": "曹魏定鼎",
    "ev-three-yiling": "夷陵之战",
    "ev-three-gaopingling": "高平陵之变",
    "ev-three-zhuge-liang": "诸葛亮北伐",
    "ev-three-zhonghui": "钟会之乱",
    "ev-three-jinrongwu": "西晋灭吴",
    "ev-three-xuanyuan": "八王之乱",

    # ---- 秦汉 ----
    "ev-qin-li-si": "秦统一六国",
    "ev-qin-great-wall": "秦长城与驰道",
    "ev-han-chu-jiang": "楚汉相争",
    "ev-han-chimei": "文景之治",
    "ev-han-donghan": "东汉建立",
    "ev-han-wangmang": "王莽篡汉",
    "ev-han-wangtian": "王莽托古改制",
    "ev-han-green-forest": "绿林起义",
    "ev-han-red-brow": "赤眉起义",
    "ev-han-wangmang-fall": "新朝灭亡",
    "ev-han-east-cao-cao": "曹操迎献帝都许",
    "ev-han-zhangheng": "张衡与浑天仪",
    "ev-han-liu-yu": "刘禹锡与陋室铭",

    # ---- 先秦 ----
    "ev-zhou-baijia": "百家争鸣",
    "ev-zhou-de-xing": "周代分封与宗法",
    "ev-zhou-bianfa": "战国变法",
    "ev-zhou-baiqiao": "白桥之战",
    "ev-zhou-sun-tzu": "孙武与《孙子兵法》",
    "ev-zhou-fenghuo": "烽火戏诸侯",
    "ev-xia-erlitou": "二里头遗址",
    "ev-xia-founding": "夏朝建立",
    "ev-shang-founding": "商朝建立",
    "ev-shang-oracle": "甲骨文与青铜器",
    "ev-pre-peking-man": "北京人",
    "ev-pre-shandongdong": "山东东夷文化",
    "ev-pre-longshan": "龙山文化",
    "ev-pre-yu": "大禹治水传说",
    "ev-pre-huangdi": "黄帝传说",

    # ---- 五代十国 ----
    "ev-wudai-yanyun": "燕云十六州割让与后晋建立",
    "ev-wudai-han": "后汉建立",
    "ev-wudai-shizong": "后周世宗改革",
    "ev-wudai-wu": "吴国建立",
    "ev-wudai-wuyue": "吴越建国",
    "ev-wudai-min": "闽国建立",
    "ev-wudai-nantang": "南唐建立",
    "ev-wudai-nanhan": "南汉建立",
    "ev-wudai-nanping": "荆南建国",
    "ev-wudai-10guo": "五代十国",
    "ev-wudai-liang": "后梁建立",
    "ev-wudai-tang": "后唐建立",
    "ev-wudai-jin": "后晋建立",
    "ev-wudai-zhou": "后周建立",
    "ev-wudai-houzhou": "后周世宗改革",

    # ---- 近代：抗日战争与解放战争 ----
    "ev-modern-zhangxun": "张勋复辟",
    "ev-modern-hugu": "护国运动",
    "ev-modern-jiu-yi-ba": "九一八事变",
    "ev-modern-jiu-ba": "九一八事变",
    "ev-modern-pingxingguan": "平型关大捷",
    "ev-modern-taierzhuang": "台儿庄战役",
    "ev-modern-baihui": "百团大战",
    "ev-modern-jiangkou": "江口战役",
    "ev-modern-chongqing-talk": "重庆谈判",
    "ev-modern-civil-war": "解放战争",
    "ev-modern-jinping": "锦州战役",
    "ev-modern-liaoshen": "辽沈战役",
    "ev-modern-huaihai": "淮海战役",
    "ev-modern-pingjin": "平津战役",
    "ev-modern-crossing": "渡江战役",
    "ev-modern-yuan-shikai": "袁世凯窃取革命果实",
    "ev-modern-empire": "洪宪帝制",
    "ev-modern-provisional": "南京临时政府成立",

    # ---- 新中国：具体事件 ----
    "ev-prc-korean-war": "抗美援朝战争",
    "ev-prc-socialist-transform": "社会主义改造完成",
    "ev-prc-great-leap": "大跃进运动",
    "ev-prc-dongfanghong": "东方红一号卫星发射",
    "ev-prc-henan-village": "河南兰考焦桐的治理",
    "ev-prc-southern-tour": "南方谈话",
    "ev-prc-socialist-market": "社会主义市场经济体制确立",
    "ev-prc-shenzhen": "深圳经济特区建设",
    "ev-prc-carbon": "碳达峰碳中和目标提出",
    "ev-prc-tianwen": "天问一号火星探测",
    "ev-prc-chang-e-five": "嫦娥五号月球采样返回",

    # ---- 金 ----
    "ev-jin-taiping": "金朝与南宋的对峙",
    "ev-jin-dongjin": "金朝东进与宋金战争",
    "ev-jin-taoyuanming": "金世宗完颜雍与治隆唐宋",
    "ev-jin-lanting": "金朝《贞观遗规》与皇统",

    # ---- 秦汉隋与五代：具体事件 ----
    "ev-sui-mo-chen": "隋末农民起义",
    "ev-sui-da-yunhe": "隋朝开凿大运河",
    "ev-sui-yanggong": "隋炀帝时期",
    "ev-wudai-li-yu": "南唐后主李煜与亡国",
    "ev-wudai-houjin": "后晋建立",
    "ev-wudai-houtang": "后唐建立",
    "ev-weijin--wei": "曹魏政权",
    "ev-weijin-buddhism": "佛教传入与魏晋南北朝",
    "ev-qin-er-shi": "秦始皇二世而亡",
    "ev-qin-chen-shihuang": "秦始皇统一六国",
    "ev-han-xinnong": "王莽托古改制与新朝建立",
    "ev-han-huangjin": "黄金时代与西汉极盛",
    "ev-han-danggu": "党锢之祸与清议",

    # ---- 五代与辽的建国 ----
    "ev-wudai-song-founding": "宋朝建立",
    "ev-wudai-chu": "楚国建立",
    "ev-wudai-shu": "蜀国建立",
    "ev-liao-founding": "辽朝建立",
    "ev-liao-fall": "辽朝灭亡",
    "ev-wudai-han-founding": "后汉建立",
    "ev-wudai-wu-founding": "吴国建立",
    "ev-wudai-nantang-founding": "南唐建立",
    "ev-wudai-jin-founding": "后晋建立",
    "ev-wudai-tang-founding": "后唐建立",
    "ev-wudai-zhou-founding": "后周建立",
    "ev-wudai-liang-founding": "后梁建立",
    "ev-liao-kaixi": "辽与西夏的关系",
    "ev-song-liao-war": "宋辽战争",
    "ev-liao-fall-jin": "辽亡与金朝崛起",
    "ev-song-jin-fall": "金朝灭亡",
    "ev-qing-nivchu": "清朝立国与入关",
    "ev-prc-land-reform": "土地制度改革",
    "ev-prc-civilization": "文化自信与两个结合",
    "ev-han-dongzhongshu": "董仲舒与罢黜百家",
}


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    renamed = 0
    left = []
    for e in data.get("events") or []:
        name = e.get("name") or ""
        if not re.search(r"[A-Za-z]", name):
            continue
        new = EVENT_NAMES.get(e["id"])
        if not new:
            slug = e["id"][3:].replace("-", " ") if e["id"].startswith("ev-") else e["id"]
            new = EVENT_NAMES.get(slug)
        if new:
            old = name
            e["name"] = new
            for field in ("detail", "summary"):
                v = e.get(field) or ""
                if old in v:
                    e[field] = v.replace(old, new)
            renamed += 1
        else:
            left.append((e["id"], name))

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: renamed {renamed} events, still-latin {len(left)}")
    for i in left[:30]:
        print("   ", i)


if __name__ == "__main__":
    main()
