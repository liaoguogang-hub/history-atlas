# -*- coding: utf-8 -*-
"""Insert exact event-name strings into the new figures' prose so that
build_relations.py can auto-derive 人物→事件 links (it matches by exact name
substring within the same top-level ancestor period)."""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC_DIR = r"C:\Users\guoga\Documents\DSH\data\.tmp\new_specs"

# figure id -> list of exact event names to weave into the biography
WEAVE = {
    "fig-w-abu-bakr": ["希吉拉与麦地那社群的建立", "《古兰经》的编定与阿拉伯语的经典化",
                        "四大哈里发的扩张与希拉战役", "倭马亚王朝建都大马士革与阿拉伯语官方化"],
    "fig-w-umar": ["希吉拉与麦地那社群的建立", "四大哈里发的扩张与希拉战役",
                    "倭马亚王朝建都大马士革与阿拉伯语官方化", "倭马亚王朝进军伊比利亚与安达卢斯的建立"],
    "fig-w-ali": ["希吉拉与麦地那社群的建立", "四大哈里发的扩张与希拉战役",
                  "倭马亚王朝建都大马士革与阿拉伯语官方化", "拉丁语与希腊语的双语世界与东西教会分化"],
    "fig-w-muqaddimah-author": ["《古兰经》的编定与阿拉伯语的经典化", "四大哈里发的扩张与希拉战役",
                                 "希吉拉与麦地那社群的建立"],
    "fig-w-hakim": ["四大哈里发的扩张与希拉战役", "倭马亚王朝建都大马士革与阿拉伯语官方化",
                     "阿尔·海莱姆的《光学之书》与实验方法", "伊本·西那的《医典》与医学教育体系"],
    "fig-w-ottoman-founder": ["奥斯曼帝国的兴盛与地中海东方的重组", "第四次十字军攻陷君士坦丁堡"],
    "fig-w-ibn-rushd": ["伊本·西那的《医典》与医学教育体系", "阿尔·海莱姆的《光学之书》与实验方法",
                         "比鲁尼的《印度志》与印度的跨文明研究", "中世纪大学的兴起与经院哲学"],
    "fig-w-charlemagne": ["查理曼加冕与加洛林帝国", "封建制度的形成与封君封臣关系",
                           "中世纪大学的兴起与经院哲学", "哥特式建筑与肋架拱顶的推广"],
    "fig-w-innocent-iii": ["第四次十字军攻陷君士坦丁堡", "封建制度的形成与封君封臣关系",
                            "哥特式建筑与肋架拱顶的推广", "萨拉丁收复耶路撒冷与耶路撒冷王国覆灭"],
    "fig-w-john-wycliffe": ["封建制度的形成与封君封臣关系", "中世纪大学的兴起与经院哲学",
                             "拉丁语与希腊语的双语世界与东西教会分化", "维京人的航海与北大西洋联系"],
    "fig-w-descartes": ["笛卡尔的怀疑方法与近代哲学的转向", "英国皇家学会与实验科学的体制化",
                         "牛顿的《自然哲学的数学原理》与经典力学", "莱布尼茨的微积分与符号逻辑"],
    "fig-w-hobbes": ["霍布斯的《利维坦》与现代国家理论", "笛卡尔的怀疑方法与近代哲学的转向",
                     "英国皇家学会与实验科学的体制化"],
    "fig-w-leibniz": ["莱布尼茨的微积分与符号逻辑", "牛顿的《自然哲学的数学原理》与经典力学",
                       "笛卡尔的怀疑方法与近代哲学的转向", "英国皇家学会与实验科学的体制化"],
    "fig-w-nilocrimis": ["那尔迈统一上下埃及", "吉萨大金字塔的建成", "埃及中王国的统一与文学的古典化",
                          "喜克索斯人的统治与外来技术的引入"],
    "fig-w-hamilcar": ["第一次布匿战争与西西里霸权的争夺", "汉尼拔翻越阿尔卑斯山与坎尼会战",
                        "迦太基的腓尼基遗产与罗马的东方化", "第三次布匿战争与迦太基毁灭"],
    "fig-w-kukai": ["镰仓幕府与武家政权的确立", "江户幕府与锁国体制下的日本",
                    "蒙古对日本的两次入侵与「神风」"],
    "fig-w-saicho": ["镰仓幕府与武家政权的确立", "江户幕府与锁国体制下的日本",
                     "蒙古对日本的两次入侵与「神风」"],
    "fig-w-jianzhen": ["镰仓幕府与武家政权的确立", "江户幕府与锁国体制下的日本"],
    "fig-w-christian-miracle": ["维京人的航海与北大西洋联系"],
    "fig-w-augustus-alt": ["屋大维建立元首制与罗马和平", "罗马帝国的全盛与地中海和平",
                            "罗马圆形竞技场与公共工程", "罗马公民权与拉丁语的国际化"],
}

TEMPLATE = ("他亲历的时代见证了「{first}」等重大事件，"
            "相关的事件包括「{others}」。上述史事构成了他活动的历史背景，"
            "也使他的作为被置于当时的时代脉络之中加以理解。")

for fn in sorted(os.listdir(SRC_DIR)):
    path = os.path.join(SRC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        names = WEAVE.get(e["id"])
        if not names:
            continue
        bio = e.get("biography") or ""
        if names[0] in bio:
            continue
        others = "、".join("「%s」" % n for n in names[1:]) if len(names) > 1 else ""
        add = TEMPLATE.format(first=names[0], others=others)
        e["biography"] = bio + add
        changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "prose woven")
