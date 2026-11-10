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
    ],
}


def year_in(a, b, y):
    if not isinstance(a, int) or not isinstance(b, int):
        return False
    return a <= y <= b


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

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: reassigned {moved} figures by their life years")


if __name__ == "__main__":
    main()
