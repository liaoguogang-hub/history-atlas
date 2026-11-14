import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 顶层时期分组：只有同一组内的时期才可能成为候选，
# 避免出现「孔子落在新巴比伦王朝」这类跨文明的错配。
GROUP = {
    "china": [
        "cn-prehistory", "cn-xia-shang", "cn-zhou-west", "cn-zhou-east",
        "cn-qin", "cn-han", "cn-wei-jin-nanbei", "cn-sui-tang", "cn-wudai",
        "cn-song-liao-jin", "cn-yuan", "cn-ming", "cn-qing", "cn-modern",
        "cn-prc",
    ],
    "world": [
        "w-prehistory", "w-ancient-near-east", "w-ancient-south-asia",
        "w-ancient-china", "w-classical-greece", "w-hellenistic", "w-roman",
        "w-post-roman", "w-medieval", "w-renaissance", "w-early-modern",
        "w-modern", "w-contemporary",
        # 区域专题
        "w-old-world", "w-america-precol", "w-africa-west", "w-africa-east",
        "w-mesoamerica", "w-andes", "w-east-asia", "w-korea", "w-japan",
        "w-southeast-asia", "w-oceania", "w-near-east-persian",
        "w-han-tang", "w-tang-song", "w-ming-qing",
        # 南亚/东南亚/非洲/拉美的编年时期（v1.7.0 与 v2.0.0 新增）。
        # 必须登记在此，否则这些时期不在候选池，人物会被归到欧美主导的时期去。
        "w-medieval-south-asia", "w-mughal",
        "w-medieval-southeast-asia", "w-modern-southeast-asia",
        "w-modern-south-asia", "w-modern-africa", "w-latin-america",
    ],
}


# ---- 地区专题时期：只能容纳「明确属于该地区」的人物 ----
# 这些时期是按地理划分的容器（东南亚、南亚、非洲、拉美…），
# 若允许按生卒年兜底塞人，就会把黑格尔、惠灵顿、董必武放进「东南亚」。
# 兜底逻辑（同组找不到 → 放宽到全时期）必须跳过它们。
REGION_PERIODS = {
    "w-medieval-south-asia", "w-modern-south-asia", "w-mughal",
    "w-medieval-southeast-asia", "w-southeast-asia", "w-modern-southeast-asia",
    "w-modern-africa", "w-africa-west", "w-africa-east", "w-old-world",
    "w-latin-america", "w-maya", "w-mesoamerica", "w-andes",
    "w-america-precol", "w-east-asia", "w-korea", "w-japan", "w-oceania",
    "w-near-east-persian", "w-han-tang", "w-tang-song", "w-ming-qing",
    "w-ancient-china", "w-cc-medieval", "w-cc-classical", "w-cc-industrial",
    "w-cc-oceanic", "w-cc-contemporary", "w-cc-prehistoric",
}


def year_in(a, b, y):
    if not isinstance(a, int) or not isinstance(b, int):
        return False
    return a <= y <= b


# ---- 显式覆盖名单：生于某时期、但历史地位属于另一时期的人物 ----
# 键=人物 id，值=目标 periodId。
# 仅用于「按生卒年归位会明显失真」的个案，正常情况下应让算法自行推断。
PERIOD_OVERRIDE = {
    # 生于两次世界大战期间(1914-1945)，但成就完全在战后 —— 归「科技时代」
    "fig-buzz-aldrin": "w-tech-era",        # 1969 年登月
    "fig-yuri-gagarin": "w-tech-era",       # 1961 年首次载人航天
    "fig-james-watson": "w-tech-era",       # 1953 年 DNA 双螺旋
    "fig-rosalind-franklin": "w-tech-era",  # 1952 年 X 射线衍射照片
    "fig-tu-youyou": "w-tech-era",          # 1970 年代发现青蒿素
    "fig-neil-armstrong": "w-tech-era",     # 1969 年登月
    # 冷战政治家 —— 归「冷战时期」
    "fig-mandela": "w-cold-war",            # 1994 年当选南非总统
    "fig-john-f-kennedy": "w-cold-war",     # 冷战总统
    "fig-nasser": "w-cold-war",             # 1952 年政变、1956 年苏伊士运河
    "fig-gamal-abdel-nasser": "w-cold-war", # 同上（实际 id）
    "fig-zzbq5-mandela": "w-cold-war",      # 同上（实际 id）
    # 源分片历史遗留的错误 periodId（被错标为东南亚，实际是英国人）
    "fig-william-wilberforce": "w-modern",  # 英国废奴运动领袖 1754-1833
    "fig-charles-ellington": "w-modern",    # 威灵顿公爵，滑铁卢 1769-1852
    # 拉丁美洲独立人物：生于 1800 年前，但历史地位属于拉美时期
    "fig-zzbq23-hidalgo": "w-latin-america",  # 墨西哥独立之父 1753-1811
    "fig-zzbq23-pedro": "w-latin-america",    # 巴西独立 1798-1834
    "fig-zzbq8-bolivar": "w-latin-america",   # 南美解放者 1783-1830
    "fig-zzbq15-sanmartin": "w-latin-america",# 南美解放者 1778-1850
    "fig-zzbq15-toussaint": "w-latin-america",# 海地革命 1743-1803
    "fig-salvador-allende": "w-latin-america",# 智利总统 1908-1973
    # 东南亚：生于 1600 年前的 VOC 总督，历史地位属于东南亚贸易时代
    "fig-zzbq23-coen": "w-southeast-asia",    # 巴达维亚建立者 1587-1629
    # 源数据中 periodId 被错标到无关地区的人物（v2.4.0 修复）
    "fig-jiang-ziya": "w-ancient-china",      # 姜子牙：周朝开国功臣，曾被错标为"古代非洲"
    "fig-modu-chanyu": "w-ancient-china",     # 冒顿单于：匈奴，曾被错标为"朝鲜"
    "fig-pericles": "w-classical-greece",     # 伯里克利：雅典，曾被错标为"近东波斯"
    "fig-euripides-2": "w-classical-greece",  # 索福克勒斯（id 命名有误），曾被错标为"近东波斯"
    "fig-herodotus": "w-classical-greece",    # 希罗多德：希腊，曾被错标为"近东波斯"
    "fig-victoria": "w-imperialism",          # 维多利亚女王：在位至 1901，归帝国主义时代
    # ---- 中国近现代：按主要政治生涯归位，而非出生年 ----
    # 这些人物生于晚清(1820-1912)区间内，但历史地位属于民国或共和国。
    # 只按生卒年归位会把他们全部塞进"清后期"，使 cn-qing-late 堆积 33 人，
    # 而"民国""中华人民共和国"时期几乎为空。
    "fig-mao-zedong": "cn-prc-early",
    "fig-zhou-enlai": "cn-prc-early",
    "fig-zzbq2-zhude": "cn-prc-early",
    "fig-liu-shaoqi": "cn-prc-early",
    "fig-peng-dehuai": "cn-prc-early",
    "fig-liu-bocheng": "cn-prc-early",
    "fig-zzbq3-chenyun": "cn-prc-early",
    "fig-zzbq3-he-long": "cn-prc-early",
    "fig-zzbq3-ye-ting": "cn-prc-early",
    "fig-deng-xiaoping": "cn-prc-reform",
    "fig-song-jiaoren": "cn-modern-republic",
    "fig-huang-xing": "cn-modern-republic",
    "fig-cai-e": "cn-modern-republic",
    "fig-duan-qirui": "cn-modern-republic",
    "fig-hu-shi": "cn-modern-republic",
    "fig-cai-yuanpei": "cn-modern-republic",
    "fig-zhang-taiyan": "cn-modern-republic",
    "fig-zhou-shuren": "cn-modern-republic",
    "fig-zhang-xueliang": "cn-modern-anti-japan",
    "fig-li-zongren": "cn-modern-anti-japan",
    # ---- 三国：生于东汉末(155-185)，但历史地位属于三国 ----
    # 只按生卒年归位会把全部三国人物塞进"东汉"(cn-han-east)，
    # 使该时期堆积 54 人，而"三国"时期 0 人物。
    "fig-han-east-cao-cao": "cn-three-wei",
    "fig-han-east-cao-pi": "cn-three-wei",
    "fig-han-east-cao-rui": "cn-three-wei",
    "fig-sima-yi": "cn-three-wei",
    "fig-sima-zhao": "cn-three-wei",
    "fig-deng-ai": "cn-three-wei",
    "fig-zhong-hui": "cn-three-wei",
    "fig-guo-jia": "cn-three-wei",
    "fig-xun-yu": "cn-three-wei",
    "fig-liu-bei": "cn-three-shu",
    "fig-zhuge-liang": "cn-three-shu",
    "fig-guan-yu": "cn-three-shu",
    "fig-zhang-fei": "cn-three-shu",
    "fig-zhao-yun": "cn-three-shu",
    "fig-jiang-wei": "cn-three-shu",
    "fig-sunquan": "cn-three-wu",
    "fig-zhou-yu": "cn-three-wu",
    "fig-lu-su": "cn-three-wu",
    "fig-lu-xun": "cn-three-wu",
    "fig-lv-meng": "cn-three-wu",
    "fig-taishi-ci": "cn-three-wu",
    # ---- 宋辽金：开国皇帝与朝代归属 ----
    "fig-zhao-kuangyin": "cn-song-north",   # 宋太祖，原误挂辽朝
    "fig-zhao-guangyi": "cn-song-north",    # 宋太宗，原误挂辽朝
    "fig-suo-shi": "cn-qing-early",         # 索额图（康熙朝），原误挂明朝
}


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    periods = data["periods"]
    scope = data.get("scope")
    by_id = {p["id"]: p for p in periods}

    # 顶层分组 → 该组下所有时期（含子时期）
    group_periods = {}
    for g in GROUP.get(scope, []):
        if g not in by_id:
            continue
        members = [g]
        gp = by_id[g]
        for q in periods:
            if q.get("parentId") == g:
                members.append(q["id"])
        # 再收一层子时期
        for q in periods:
            if q.get("parentId") in members:
                members.append(q["id"])
        group_periods[g] = [by_id[m] for m in members if m in by_id]

    moved = 0
    for f in data.get("figures") or []:
        by = f.get("birthYear")
        dy = f.get("deathYear")
        if not isinstance(by, int):
            continue
        cur = f.get("periodId")

        # 当前时期所属顶层分组
        cur_top = None
        for g, members in group_periods.items():
            if any(m["id"] == cur for m in members):
                cur_top = g
                break

        members = group_periods.get(cur_top, []) if cur_top else []
        if not members:
            members = periods

        # 若当前时期本身就能容纳人物的生卒年，就不动它——
        # 数据方已经把它放在正确的分支里，不应因为别的时期「更窄」而挪走。
        cp = by_id.get(cur)
        if cp:
            cs, ce = cp.get("startYear"), cp.get("endYear")
            if year_in(cs, ce, by) and (
                    not isinstance(dy, int) or year_in(cs, ce, dy)
                    or (ce - cs) <= 0 or dy <= ce + (ce - cs)):
                continue

        cands = []
        for q in members:
            qs, qe = q.get("startYear"), q.get("endYear")
            if not year_in(qs, qe, by):
                continue
            if isinstance(dy, int) and not year_in(qs, qe, dy):
                span = qe - qs
                if span <= 0 or dy > qe + span:
                    continue
            cands.append(q)

        # 同组内找不到（例如人物被误挂在史前分支），则放宽到全时期，
        # 但排除明显跨越千年的超长时期，优先落到更具体的分支。
        if not cands:
            for q in periods:
                qs, qe = q.get("startYear"), q.get("endYear")
                if not year_in(qs, qe, by):
                    continue
                if isinstance(dy, int) and not year_in(qs, qe, dy):
                    span = qe - qs
                    if span <= 0 or dy > qe + span:
                        continue
                if (qe - qs) > 1200:
                    continue          # 跨度过大的时期过于笼统
                if q["id"] in REGION_PERIODS:
                    continue          # 地区专题时期不接受兜底塞入
                cands.append(q)

        if not cands:
            continue
        best = min(cands, key=lambda q: q["endYear"] - q["startYear"])
        if best["id"] != cur:
            f["periodId"] = best["id"]
            moved += 1

    # ---- 显式覆盖：按生卒年归位无法表达「成名期」的个案 ----
    # 有些人物出生于某个窄时期（如两次世界大战 1914-1945），但其历史地位来自
    # 战后成就（登月、DNA 双螺旋、青蒿素、南非民主化）。仅按生卒年归位会把他们
    # 塞进「两次世界大战」，使该时期的代表人物列表严重失真。
    # 这里以名单方式显式指定归属，优先级高于生卒年推断。
    forced = 0
    for f in data.get("figures") or []:
        target = PERIOD_OVERRIDE.get(f.get("id"))
        if target and f.get("periodId") != target:
            f["periodId"] = target
            forced += 1
    if forced:
        print(f"{path}: forced {forced} figures by explicit override")

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: reassigned {moved} figures by their life years")


if __name__ == "__main__":
    main()
