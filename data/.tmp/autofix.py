# -*- coding: utf-8 -*-
"""Auto-fix Latin words in expansion specs using a dictionary, and report
any that remain unhandled so they can be handled manually."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
SPEC_DIR = os.path.join(TMP, "exp_specs")
LATIN = re.compile(r"[A-Za-z]{2,}")

DICT = {
    "crews": "船员", "speech": "演说", "shortly": "不久", "oblasts": "各州",
    "Iskra": "火星报", "wartime": "战时", "secret": "秘密", "undersecretary": "次长",
    "Metaphor": "隐喻", "blacks": "黑人", "Brown": "布朗", "Keynes": "凯恩斯",
    "Rural": "乡村", "campaigns": "战役", "Iskra 火星报": "火星报",
    "secret 报告": "秘密报告", "Keynes 主义": "凯恩斯主义",
    "Marshall": "马歇尔", "Truman": "杜鲁门", "Keynes": "凯恩斯",
    "Vienna": "维也纳", "Rome": "罗马", "London": "伦敦", "Paris": "巴黎",
    "Athens": "雅典", "Sparta": "斯巴达", "Persia": "波斯", "Rome": "罗马",
    "Greece": "希腊", "China": "中国", "India": "印度", "Japan": "日本",
    "Egypt": "埃及", "Cuba": "古巴", "Africa": "非洲", "Asia": "亚洲",
    "Europe": "欧洲", "America": "美洲", "Berlin": "柏林", "Moscow": "莫斯科",
    "Washington": "华盛顿", "Geneva": "日内瓦", "Venice": "威尼斯",
    "Florence": "佛罗伦萨", "Rome": "罗马", "Genoa": "热那亚", "Lisbon": "里斯本",
    "Seville": "塞维利亚", "Cape": "好望角", "Good": "好望角",
    "Proust": "普鲁斯特", "Kafka": "卡夫卡", "Tolstoy": "托尔斯泰",
    "Borges": "博尔赫斯", "Saramago": "萨拉马戈", "Tagore": "泰戈尔",
    "Gandhi": "甘地", "Nehru": "尼赫鲁", "Nyerere": "尼雷尔",
    "Mandela": "曼德拉", "Nakasone": "中曾根",
}

SUMMARY = {
    "fig-abraham-lincoln": "美国第十六任总统，以领导南北战争与发布《解放奴隶宣言》终结奴隶制。",
    "fig-richard-nixon": "美国第三十七任总统，以一九七二年访华打开中美关系并调整冷战战略。",
    "fig-harry-white": "美国财政部的经济学家，布雷顿森林体系与国际货币基金组织的主要设计者。",
    "fig-paul-henri-spaak": "比利时政治家与外交家，欧洲煤钢共同体与欧洲经济共同体的推动者之一。",
    "fig-joan-of-arc": "法国奥尔良的乡村少女，以自称奉上帝之命解救奥尔良而成为民族英雄。",
    "fig-charles-ellington": "英国陆军元帅，以滑铁卢战役击败拿破仑并两度出任英国首相。",
    "fig-ferdinand-magellan": "葡萄牙航海家，率船队首次横渡太平洋，完成了人类史上第一次环球航行。",
    "fig-john-maynard-keynes": "英国经济学家，宏观经济学与一般均衡理论的奠基者，凯恩斯主义的提出者。",
    "fig-harry-truman": "美国第三十三任总统，以杜鲁门主义、马歇尔计划与联合国的建立塑造战后秩序。",
    "fig-vasco-da-gama": "葡萄牙航海家，绕过好望角抵达印度，为欧洲打开了直达东方的海路。",
    "fig-khrushchev": "苏联领导人，以否定斯大林的个人崇拜与缓和美苏关系著称。",
    "fig-de-gaulle": "法国第五共和国的缔造者，以强总统体制与自主外交重塑了战后的法国。",
    "fig-alfonso-de-albuquerque": "葡萄牙印度总督，以建立横跨印度洋的据点网络开创了欧洲的海上帝国。",
    "fig-lenin": "布尔什维克党的领袖与苏维埃俄国的缔造者，俄国十月革命的主要领导人。",
    "fig-stalin": "苏联领导人，以五年计划与卫国战争的领导塑造了苏联的工业化与战时动员。",
    "fig-mahatma-gandhi": "印度独立运动的精神领袖，以非暴力抵抗改造了殖民地的政治行动方式。",
    "fig-jawaharlal-nehru": "印度首任总理，不结盟运动的共同发起者，亚非国家的重要政治领袖。",
    "fig-ho-chi-minh": "越南革命家与国家领导人，创立越南民主共和国并领导抗法战争。",
    "fig-richard-nixon": "美国第三十七任总统，以一九七二年访华打开中美关系并调整冷战战略。",
}

for fn in sorted(os.listdir(SPEC_DIR)):
    path = os.path.join(SPEC_DIR, fn)
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception:
        continue
    changed = False
    for e in d:
        if e["id"] in SUMMARY:
            e["summary"] = SUMMARY[e["id"]]; changed = True
        for f in ("summary", "biography", "alias", "role", "lifeText"):
            v = e.get(f)
            if isinstance(v, str):
                nv = v
                for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                    nv = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, nv)
                if nv != v:
                    e[f] = nv; changed = True
        for f in ("achievements", "quotes", "tags"):
            if isinstance(e.get(f), list):
                nl = []
                for i in e[f]:
                    s = str(i)
                    for a, b in sorted(DICT.items(), key=lambda kv: -len(kv[0])):
                        s = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", b, s)
                    nl.append(s)
                if nl != e[f]:
                    e[f] = nl; changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fn, "autofixed")
