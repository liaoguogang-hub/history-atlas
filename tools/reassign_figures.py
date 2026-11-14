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
