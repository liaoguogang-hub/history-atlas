import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

# 跨文明事件的时期归属规则。
#
# 背景：原始分片把大量「跨文明」事件（ev-cc-*）与各文明自身的事件
# 混写在少数几个时期里，导致「朝鲜半岛」时期下出现哥伦布、达伽马、
# 罗塞塔石碑这类明显错位的内容。
#
# 规则按事件 id 前缀与名称语义判定，优先级从高到低。

PREFIX_RULES = [
    # 中国与东亚
    ("ev-cc-han-", "w-han-tang"), ("ev-cc-khitan", "w-tang-song"),
    ("ev-cc-song-jin", "w-tang-song"), ("ev-cc-gutenberg-cjk", "w-tang-song"),
    ("ev-cc-china-europe-jesuit", "w-renaissance"),
    ("ev-cc-columbus-tianxia", "w-renaissance"),
    ("ev-cc-yamane-crossroads", "w-early-modern"),
    ("ev-cc-tribute-system-china", "w-early-modern"),
    ("ev-cc-aboriginal-silk-australia", "w-old-world"),
    ("ev-cc-hanse-", "w-medieval"),
    ("ev-cc-silk-road-envoys", "w-han-tang"),
    ("ev-cc-han-scythian-routes", "w-han-tang"),
    ("ev-cc-silk-maritime", "w-early-modern"),
    ("ev-cc-silk-cotton-global", "w-early-modern"),
    ("ev-cc-ottoman-silk-road", "w-early-modern"),
    ("ev-cc-iraq-silk", "w-medieval-islam"),
    ("ev-cc-timur-baghdad", "w-mongol-empire"),
    ("ev-cc-rashid-al-din", "w-mongol-empire"),
    ("ev-cc-isaac-almohad", "w-medieval-islam"),
    ("ev-cc-mongol-christian-relations", "w-mongol-empire"),
    ("ev-cc-mongol-pax-mongolica", "w-mongol-empire"),
    ("ev-cc-black-death", "w-medieval"),
    ("ev-cc-gunpowder-west", "w-medieval"),
    ("ev-cc-byzantine-intellectual-flow", "w-renaissance"),
    ("ev-cc-italy-ottoman-guns", "w-renaissance"),
    ("ev-cc-choirophthon-empire", "w-early-modern"),
    ("ev-cc-philippine-galleon", "w-early-modern"),
    ("ev-cc-philippines-mexico-galleon", "w-early-modern"),
    ("ev-cc-columbus-exchange", "w-early-modern"),
    ("ev-cc-magellan-route", "w-early-modern"),
    ("ev-cc-cape-route", "w-early-modern"),
    ("ev-cc-spice-island", "w-early-modern"),
    ("ev-cc-marco-medical", "w-medieval"),
    ("ev-cc-gutenberg-missionary-print", "w-early-modern"),
    ("ev-cc-indian-ocean-monsoon-trade", "w-medieval"),
    ("ev-cc-france-britain-medieval", "w-medieval"),
    ("ev-cc-hindutemple-tantric", "w-ancient-south-asia"),
    ("ev-cc-cc-panthera-india-rome", "w-ancient-south-asia"),
    ("ev-cc-panthera-india-rome", "w-ancient-south-asia"),
    ("ev-cc-caribbean-slavery", "w-early-modern"),
    ("ev-cc-india-british-railway", "w-modern"),
    ("ev-cc-world-expo", "w-modern"),
    ("ev-cc-telegraph-ocean", "w-modern"),
    ("ev-cc-telecom-diaspora", "w-modern"),
    ("ev-cc-world-rugby-japan", "w-contemporary"),
    ("ev-cc-colonized-knowledge", "w-modern"),
    ("ev-cc-hanse-iceland", "w-post-roman"),
    # 具体文明
    ("ev-egypt-", "w-egypt-old"),
    ("ev-kushan-", "w-ancient-south-asia"),
    ("ev-satavahana-", "w-ancient-south-asia"),
    ("ev-qin-unify", "w-ancient-china"),
    ("ev-han-founding", "w-han-tang"),
    ("ev-han-wudi", "w-han-tang"),
    ("ev-han-zhangqian", "w-han-tang"),
    ("ev-han-buddhism", "w-han-tang"),
    ("ev-han-end", "w-han-tang"),
    ("ev-han-roman-buddhism-parallel", "w-han-tang"),
    ("ev-three-kingdoms", "w-han-tang"),
    ("ev-jin-unify-nanbeiguo", "w-han-tang"),
    ("ev-sui-tang", "w-han-tang"),
    ("ev-med-kor-goryeo", "w-korea"),
]

# 名称关键词 → 时期（用于 id 前缀匹配不到时）
NAME_RULES = [
    ("罗塞塔", "w-egypt-old"),
    ("埃及", "w-egypt-old"),
    ("贵霜", "w-ancient-south-asia"),
    ("犍陀罗", "w-ancient-south-asia"),
    ("孔雀", "w-ancient-south-asia"),
    ("印度", "w-ancient-south-asia"),
    ("高丽", "w-korea"),
    ("朝鲜", "w-korea"),
    ("新罗", "w-korea"),
    ("汉唐", "w-han-tang"),
    ("秦", "w-ancient-china"),
    ("汉", "w-han-tang"),
    ("唐", "w-han-tang"),
    ("宋", "w-tang-song"),
    ("辽", "w-tang-song"),
    ("金", "w-tang-song"),
    ("西夏", "w-tang-song"),
    ("蒙古", "w-mongol-empire"),
    ("帖木儿", "w-mongol-empire"),
    ("奥斯曼", "w-early-modern"),
    ("拜占庭", "w-renaissance"),
    ("哥伦布", "w-early-modern"),
    ("麦哲伦", "w-early-modern"),
    ("达伽马", "w-early-modern"),
    ("西班牙", "w-early-modern"),
    ("葡萄牙", "w-early-modern"),
    ("马尼拉", "w-early-modern"),
    ("美洲", "w-america-precol"),
    ("安第斯", "w-andes"),
    ("玛雅", "w-maya"),
    ("中美洲", "w-mesoamerica"),
    ("非洲", "w-old-world"),
    ("日本", "w-japan"),
    ("朝鲜半岛", "w-korea"),
    ("朝鲜", "w-korea"),
    ("高丽", "w-korea"),
    ("新罗", "w-korea"),
    ("波斯", "w-near-east-persian"),
    ("伊斯兰", "w-medieval-islam"),
    ("哈里发", "w-post-roman"),
    ("罗马", "w-roman"),
    ("希腊", "w-classical-greece"),
    ("基督教", "w-post-roman"),
    ("维京", "w-post-roman"),
    ("冰岛", "w-post-roman"),
    ("印刷", "w-renaissance"),
    ("哥伦布", "w-early-modern"),
    ("大西洋", "w-early-modern"),
    ("奴隶贸易", "w-early-modern"),
    ("香料", "w-early-modern"),
    ("丝绸之路", "w-han-tang"),
    ("季风", "w-medieval"),
    ("印度洋", "w-medieval"),
    ("电报", "w-modern"),
    ("铁路", "w-modern"),
    ("博览会", "w-modern"),
    ("侨民", "w-modern"),
    ("殖民", "w-modern"),
    ("体育", "w-contemporary"),
    ("科技", "w-tech-era"),
    ("冷战", "w-cold-war"),
    ("全球化", "w-post-70s"),
    ("去殖民", "w-decolonization"),
    ("世界大战", "w-world-wars"),
    ("朝鲜战争", "w-cold-war"),
    ("越南", "w-cold-war"),
    ("苏哈托", "w-decolonization"),
    ("尼雷尔", "w-decolonization"),
    ("恩克鲁玛", "w-decolonization"),
    ("现代化", "w-post-70s"),
]

# 明确不该出现在「朝鲜半岛」等区域专题下的文明级事件前缀
REGIONAL_TOPICS = {
    "w-korea", "w-japan", "w-oceania", "w-southeast-asia", "w-east-asia",
    "w-africa-west", "w-africa-east", "w-maya", "w-mesoamerica", "w-andes",
    "w-old-world", "w-america-precol",
}


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    by_id = {p["id"]: p for p in d["periods"]}

    moved = 0
    for e in d.get("events") or []:
        cur = e.get("periodId")
        eid = e["id"]
        name = e.get("name") or ""

        target = None
        for pref, pid in PREFIX_RULES:
            if eid.startswith(pref) and pid in by_id:
                target = pid
                break
        if target is None:
            for kw, pid in NAME_RULES:
                if kw in name and pid in by_id:
                    target = pid
                    break

        if target and target != cur:
            e["periodId"] = target
            moved += 1

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{path}: reassigned {moved} events by id prefix / name rules")

    # 报告各时期的事件数
    c = collections.Counter(e.get("periodId") for e in d["events"])
    print("  events per period:")
    for pid, n in c.most_common(12):
        print(f"    {n:4d}  {pid:26s} {by_id.get(pid, {}).get('name')}")


if __name__ == "__main__":
    main()
