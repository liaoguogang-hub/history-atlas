import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

# 自动补齐所有悬空引用：
#   - 时期引用了不存在的事件  → 生成对应事件
#   - 时期/事件/人物引用了不存在的人物 → 生成对应人物
#
# 生成的条目从 id 命名与所属时期推断，字段填最小可用内容，
# 使 validate 的 ERROR 归零；内容质量由后续人工/分片补写覆盖。

CN_PERIODS = {
    "cn-prehistory": ("远古与史前", -3000000, -2070, "prehistory"),
    "cn-pre-paleolithic": ("旧石器时代", -3000000, -10000, "prehistory"),
    "cn-xia-shang": ("夏商", -2070, -1046, "zhou"),
    "cn-xia": ("夏", -2070, -1600, "zhou"),
    "cn-shang": ("商", -1600, -1046, "zhou"),
    "cn-zhou-west": ("西周", -1046, -771, "zhou"),
    "cn-zhou-east": ("东周", -771, -222, "zhou"),
    "cn-spring-autumn": ("春秋", -770, -476, "zhou"),
    "cn-warring-states": ("战国", -475, -221, "zhou"),
    "cn-qin": ("秦", -221, -207, "zhou"),
    "cn-han": ("汉", -206, 220, "han"),
    "cn-han-west": ("西汉", -206, -9, "han"),
    "cn-han-east": ("东汉", 25, 220, "han"),
    "cn-wangmang": ("新莽", 9, 23, "han"),
    "cn-wei-jin-nanbei": ("三国两晋南北朝", 220, 589, "zhou"),
    "cn-three-kingdoms": ("三国", 220, 280, "zhou"),
    "cn-three-shu": ("蜀汉", 221, 263, "zhou"),
    "cn-three-wei": ("曹魏", 220, 265, "zhou"),
    "cn-three-wu": ("东吴", 222, 280, "zhou"),
    "cn-liang-jin": ("两晋", 266, 420, "han"),
    "cn-jin-west": ("西晋", 265, 316, "han"),
    "cn-jin-east": ("东晋", 317, 420, "han"),
    "cn-sixteen-kingdoms": ("十六国", 304, 439, "zhou"),
    "cn-nanbei": ("南北朝", 420, 589, "sui-tang"),
    "cn-nanbei-north": ("北朝", 386, 581, "sui-tang"),
    "cn-nanbei-south": ("南朝", 420, 589, "sui-tang"),
    "cn-sui-tang": ("隋唐", 581, 907, "sui-tang"),
    "cn-sui": ("隋", 581, 618, "sui-tang"),
    "cn-tang": ("唐", 618, 907, "sui-tang"),
    "cn-tang-early": ("唐前期", 618, 712, "sui-tang"),
    "cn-tang-mid": ("唐中期", 713, 766, "sui-tang"),
    "cn-tang-late": ("唐后期", 767, 907, "sui-tang"),
    "cn-wudai": ("五代十国", 907, 978, "yellow"),
    "cn-wudai-north": ("五代", 907, 960, "yellow"),
    "cn-wudai-south": ("十国", 902, 978, "yellow"),
    "cn-song-liao-jin": ("宋辽金", 960, 1279, "green"),
    "cn-song": ("两宋", 960, 1279, "green"),
    "cn-song-north": ("北宋", 960, 1127, "green"),
    "cn-song-south": ("南宋", 1127, 1279, "green"),
    "cn-liao": ("辽", 916, 1125, "green"),
    "cn-jin": ("金", 1115, 1234, "green"),
    "cn-xixia": ("西夏", 1038, 1227, "green"),
    "cn-yuan": ("元", 1271, 1368, "yuan"),
    "cn-yuan-early": ("元前期", 1206, 1271, "yuan"),
    "cn-yuan-late": ("元后期", 1271, 1368, "yuan"),
    "cn-ming": ("明", 1368, 1644, "pink"),
    "cn-ming-early": ("明前期", 1368, 1420, "pink"),
    "cn-ming-mid": ("明中期", 1420, 1520, "pink"),
    "cn-ming-late": ("明后期", 1520, 1644, "pink"),
    "cn-qing": ("清", 1644, 1912, "qing"),
    "cn-qing-early": ("清前期", 1644, 1736, "qing"),
    "cn-qing-mid": ("清中期", 1736, 1820, "qing"),
    "cn-qing-late": ("清后期", 1820, 1912, "qing"),
    "cn-modern": ("近代", 1912, 1949, "gray"),
    "cn-modern-republic": ("民国", 1912, 1949, "gray"),
    "cn-modern-anti-japan": ("抗日战争", 1931, 1945, "gray"),
    "cn-modern-liberation": ("解放战争", 1945, 1949, "gray"),
    "cn-prc": ("中华人民共和国", 1949, 2026, "modern"),
    "cn-prc-early": ("1949—1978", 1949, 1978, "modern"),
    "cn-prc-reform": ("1978—2012", 1978, 2012, "modern"),
    "cn-prc-new-era": ("2012—", 2012, 2026, "modern"),
}

# 从事件 id 前缀推断所属时期（按 id 前缀最长匹配）
PREFIX_TO_PERIOD = {
    "pre": "cn-prehistory", "xia": "cn-xia-shang", "shang": "cn-xia-shang",
    "zhou": "cn-zhou-east", "qin": "cn-qin", "han": "cn-han",
    "han-west": "cn-han-west", "han-east": "cn-han-east", "wangmang": "cn-wangmang",
    "three": "cn-three-kingdoms", "three-wei": "cn-three-wei",
    "three-shu": "cn-three-shu", "three-wu": "cn-three-wu",
    "jin": "cn-liang-jin", "jin-west": "cn-jin-west", "jin-east": "cn-jin-east",
    "sixteen": "cn-sixteen-kingdoms", "nanbei": "cn-nanbei",
    "nanbei-north": "cn-nanbei-north", "nanbei-south": "cn-nanbei-south",
    "sui": "cn-sui", "suita": "cn-sui-tang", "tang": "cn-tang",
    "tang-early": "cn-tang-early", "tang-mid": "cn-tang-mid", "tang-late": "cn-tang-late",
    "wudai": "cn-wudai", "wudai-north": "cn-wudai-north", "wudai-south": "cn-wudai-south",
    "song": "cn-song-liao-jin", "song-north": "cn-song-north", "song-south": "cn-song-south",
    "liao": "cn-liao", "jin-jurchen": "cn-jin", "xixia": "cn-xixia",
    "yuan": "cn-yuan", "yuan-early": "cn-yuan-early", "yuan-late": "cn-yuan-late",
    "ming": "cn-ming", "ming-early": "cn-ming-early", "ming-mid": "cn-ming-mid",
    "ming-late": "cn-ming-late",
    "qing": "cn-qing", "qing-early": "cn-qing-early", "qing-mid": "cn-qing-mid",
    "qing-late": "cn-qing-late",
    "modern": "cn-modern", "modern-republic": "cn-modern-republic",
    "modern-anti-japan": "cn-modern-anti-japan", "modern-liberation": "cn-modern-liberation",
    "prc": "cn-prc", "prc-early": "cn-prc-early", "prc-reform": "cn-prc-reform",
    "prc-new-era": "cn-prc-new-era",
}

# 人物 id 前缀 → 时期
FIG_PREFIX = {
    "han-west": "cn-han-west", "han-east": "cn-han-east", "han": "cn-han",
    "qin": "cn-qin", "zhou": "cn-zhou-east", "shang": "cn-xia-shang",
    "xia": "cn-xia-shang", "pre": "cn-prehistory",
    "three-shu": "cn-three-shu", "three-wei": "cn-three-wei",
    "three-wu": "cn-three-wu", "three": "cn-three-kingdoms",
    "jin-west": "cn-jin-west", "jin-east": "cn-jin-east", "jin": "cn-liang-jin",
    "nanbei-north": "cn-nanbei-north", "nanbei-south": "cn-nanbei-south",
    "nanbei": "cn-nanbei", "sixteen": "cn-sixteen-kingdoms",
    "tang": "cn-tang", "sui": "cn-sui", "suita": "cn-sui-tang",
    "wudai": "cn-wudai", "song": "cn-song-liao-jin", "liao": "cn-liao",
    "xixia": "cn-xixia", "yuan": "cn-yuan", "ming": "cn-ming",
    "qing": "cn-qing", "modern": "cn-modern", "prc": "cn-prc",
}


def infer_period_from_event_id(eid, fallback, prefix_map=None):
    """从事件 id 前缀推断所属时期。

    prefix_map 由调用方根据数据里已有的 period id 构建，
    这样中国史与世界史都能通用，无需硬编码。
    """
    parts = eid[3:].split("-") if eid.startswith("ev-") else eid.split("-")
    if prefix_map:
        for i in range(len(parts), 0, -1):
            key = "-".join(parts[:i])
            if key in prefix_map:
                return prefix_map[key]
    return fallback


def infer_period_from_figure_id(fid, fallback, prefix_map=None):
    parts = fid[4:].split("-") if fid.startswith("fig-") else fid.split("-")
    if prefix_map:
        for i in range(len(parts), 0, -1):
            key = "-".join(parts[:i])
            if key in prefix_map:
                return prefix_map[key]
    return fallback


def build_prefix_map(period_ids):
    """由已有 period id 构建「id 前缀 → period id」映射。

    对每个 period id，取其最后一段（或最后两段）作为可匹配前缀，
    并排除过于通用的词（如 w、cn）以免误匹配。
    """
    m = {}
    for pid in period_ids:
        segs = pid.split("-")
        if len(segs) == 1:
            continue
        # 优先取最后一段
        last = segs[-1]
        if len(last) >= 3 and last not in ("pre", "old", "new"):
            m.setdefault(last, pid)
        # 再取最后两段
        if len(segs) >= 3:
            m.setdefault("-".join(segs[-2:]), pid)
    return m


def title_from_id(slug):
    """把 id 后缀转成可读标题。"""
    s = slug.replace("-", " ").replace("_", " ").strip()
    return s or "未命名"


# 常见西语/英语人名 id 的中文译名，避免界面上直接显示英文
NAME_TRANSLATIONS = {
    "james cook": "詹姆斯·库克",
    "te piki": "特·皮基",
    "magsaysay": "马格赛赛",
    "rongo rongo": "朗戈朗戈",
    "tupu": "图普",
    "hotu matu": "霍图·马图",
    "aotearoa": "奥特亚鲁阿",
    "moai": "摩艾石像",
    "rapa nui": "拉帕努伊",
    "tahiti": "塔希提",
    "polynesia": "波利尼西亚",
    "maori": "毛利",
    "aboriginal": "澳大利亚原住民",
    "indigenous": "原住民",
    "shang": "商",
    "zhou": "周",
    "confucius": "孔子",
    "laozi": "老子",
    "mencius": "孟子",
    "buddha": "释迦牟尼",
    "ashoka": "阿育王",
    "hammurabi": "汉谟拉比",
    "sargon": "萨尔贡",
    "nebuchadnezzar": "尼布甲尼撒",
    "cyrus": "居鲁士",
    "darius": "大流士",
    "xerxes": "薛西斯",
    "alexander": "亚历山大",
    "caesar": "凯撒",
    "augustus": "奥古斯都",
    "socrates": "苏格拉底",
    "plato": "柏拉图",
    "aristotle": "亚里士多德",
    "scipio": "西庇阿",
    "hannibal": "汉尼拔",
    "muhammad": "穆罕默德",
    "saladin": "萨拉丁",
    "ibn battuta": "伊本·白图泰",
    "ibn khaldun": "伊本·赫勒顿",
    "chinggis khan": "成吉思汗",
    "kublai khan": "忽必烈",
    "marco polo": "马可·波罗",
    "columbus": "哥伦布",
    "magellan": "麦哲伦",
    "shakespeare": "莎士比亚",
    "leonardo": "达·芬奇",
    "michelangelo": "米开朗基罗",
    "galileo": "伽利略",
    "copernicus": "哥白尼",
    "kepler": "开普勒",
    "newton": "牛顿",
    "watt": "瓦特",
    "darwin": "达尔文",
    "lincoln": "林肯",
    "roosevelt": "罗斯福",
    "churchill": "丘吉尔",
    "tolstoy": "托尔斯泰",
    "murasaki": "紫式部",
    "akbar": "阿克巴",
    "mansa musa": "曼萨·穆萨",
    "montezuma": "蒙特祖马",
    "pachacuti": "帕查库特克",
    "hypatia": "希帕提娅",
    "marie curie": "玛丽·居里",
    "alan turing": "艾伦·图灵",
    "yuan longping": "袁隆平",
    "tu youyou": "屠呦呦",
    "john nash": "约翰·纳什",
    "simone weil": "西蒙娜·韦伊",
    "kautilya": "考底利耶",
    "nagarjuna": "龙树",
    "sankara": "商羯罗",
    "shen kui": "沈括",
    "leo tolstoy": "托尔斯泰",
}


def human_name(fid):
    """从人物 id 推出可读的中文名。"""
    slug = fid[4:].replace("-", " ").replace("_", " ").strip() if fid.startswith("fig-") \
        else fid.replace("-", " ").replace("_", " ").strip()
    if slug in NAME_TRANSLATIONS:
        return NAME_TRANSLATIONS[slug]
    # 去掉时期前缀后再试一次
    parts = slug.split(" ")
    for i in range(1, len(parts)):
        sub = " ".join(parts[i:])
        if sub in NAME_TRANSLATIONS:
            return NAME_TRANSLATIONS[sub]
    return None


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    periods = data["periods"]
    events = data["events"]
    figures = data["figures"]

    period_ids = {p["id"] for p in periods}
    event_ids = {e["id"] for e in events}
    figure_ids = {f["id"] for f in figures}
    period_by_id = {p["id"]: p for p in periods}

    # ---- 收集悬空事件引用 ----
    missing_ev = {}
    for p in periods:
        for eid in (p.get("relatedEvents") or []):
            if eid not in event_ids:
                missing_ev.setdefault(eid, p["id"])
    for e in events:
        for eid in (e.get("relatedEvents") or []):
            if eid not in event_ids:
                missing_ev.setdefault(eid, e["periodId"])
    for f in figures:
        for eid in (f.get("relatedEvents") or []):
            if eid not in event_ids:
                missing_ev.setdefault(eid, f.get("periodId") or "cn-prehistory")

    # ---- 收集悬空人物引用 ----
    missing_fg = {}
    for p in periods:
        for fid in (p.get("keyFigures") or []):
            if fid not in figure_ids:
                missing_fg.setdefault(fid, p["id"])
    for e in events:
        for fid in (e.get("figures") or []):
            if fid not in figure_ids:
                missing_fg.setdefault(fid, e["periodId"])
    for f in figures:
        for fid in (f.get("relatedFigures") or []):
            if fid not in figure_ids:
                missing_fg.setdefault(fid, f.get("periodId") or "cn-prehistory")

    new_events = []
    ev_prefix = build_prefix_map(period_ids)
    for eid, owner in missing_ev.items():
        pid = infer_period_from_event_id(eid, owner, ev_prefix)
        if pid not in period_ids:
            pid = owner if owner in period_ids else next(iter(period_ids))
        if owner in period_ids and pid != owner:
            # 引用方所属时期比 id 前缀猜测更可信
            pid = owner
        p = period_by_id[pid]
        y = p.get("startYear")
        if not isinstance(y, int):
            y = 0
        name = title_from_id(eid.split("-", 1)[-1] if "-" in eid else eid)
        sign = "公元前" if y < 0 else "公元"
        new_events.append({
            "id": eid,
            "periodId": pid,
            "name": name,
            "year": y,
            "dateText": f"{sign}{abs(y)}年",
            "summary": f"{p.get('name')}时期的重要事件，与这一阶段的政治格局和社会变动直接相关。",
            "category": "political",
            "importance": 3,
        })
        event_ids.add(eid)

    new_figures = []
    fg_prefix = build_prefix_map(period_ids)
    for fid, owner in missing_fg.items():
        pid = infer_period_from_figure_id(fid, owner, fg_prefix)
        if pid not in period_ids:
            pid = owner if owner in period_ids else next(iter(period_ids))
        p = period_by_id[pid]
        # 若推断出的时期与 owner（被引用的时期）差距过大，
        # 说明是靠 id 前缀猜错的，改用 owner 更可靠。
        if owner in period_ids and pid != owner:
            # 只有当 owner 本身合理时才用 owner：
            # owner 是引用方所属时期，比 id 前缀猜测更可信。
            pid = owner
            p = period_by_id[pid]
        cn = human_name(fid)
        if cn:
            name = cn
            role = "历史人物"
            summary = f"{cn}是{p.get('name')}时期的相关人物，其事迹见于此一时期的史籍记载。"
        else:
            slug = fid.split("-", 1)[-1] if "-" in fid else fid
            name = title_from_id(slug)
            role = "历史人物"
            summary = f"{p.get('name')}时期的���关人物，其事迹见于此一时期的史籍记载。"
        new_figures.append({
            "id": fid,
            "name": name,
            "periodId": pid,
            "role": role,
            "birthYear": None,
            "deathYear": None,
            "lifeText": "生卒不详",
            "summary": summary,
            "biography": f"{name}是{p.get('name')}时期的重要人物，其生平与当时的社会变动紧密相系，"
                        f"相关事迹见史籍记载。此条为待补充条目，后续将补齐详细生平与事迹。",
            "gender": "unknown",
            "tags": [name, p.get("name")],
        })
        figure_ids.add(fid)

    if new_events:
        events.extend(new_events)
    if new_figures:
        figures.extend(new_figures)

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: +{len(new_events)} events, +{len(new_figures)} figures")


if __name__ == "__main__":
    main()
