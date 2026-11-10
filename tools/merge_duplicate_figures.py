"""合并重复的人物条目。

原始分片里同一个人物被拆成多条记录（萧衍出现 8 次、杨坚 5 次、王猛 5 次），
导致人物志里同一人反复出现，且多数副本只有一句话甚至空传记。

合并策略：
- 按 name 精确聚类
- 组内按「传记长度 → 关联数量」排序，最丰富的一条作为保留者
- 保留者缺失的字段从其余副本补齐；关联列表取并集；生卒年互补
- 全部指向副本的引用改写为保留者 id
- 删除副本

安全阀：若组内两条记录的生卒年都有值且相差超过 5 年，视为同名不同人，
不合并，只报告。
"""
import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

YEAR_TOLERANCE = 5

# 显式合并：同名且确认是同一人，但数据里的年份错得超出容错范围。
# 值为合并后应采用的正确定生卒年（None 表示留空）。
FORCE_MERGE = {
    # 拓跋珪（北魏道武帝，371—409）：两份数据生年都误作 318
    "拓跋珪": (-371, 409),
    # 陈平（？—前178）：一份生年误作 -179
    "陈平": (None, -178),
    # 仆固怀恩（？—765）：一份卒年符号写反成 -781
    "仆固怀恩": (None, 765),
}

# 名字与内容不符的条目：id -> (正确姓名, 生年, 卒年)
NAME_FIX = {
    # 传记写「沙陀人，父李克用为唐末名将」，实为后唐明宗李嗣源
    "fig-liwang-yan": ("李嗣源", 867, 933),
}

LIST_FIELDS = ("relatedEvents", "relatedFigures", "tags", "achievements", "quotes")
REQUIRED = ("name", "role", "summary", "biography")


def year_compatible(a, b):
    """两条记录的生卒年是否可视为同一人。

    除直接比较外，还容错两种脏数据：
    1. 一侧年份符号写反（史思明存成 703/761 与 None/-761）。
    2. 一侧传记为空——空壳条目没有独立信息价值，不应因为
       它记的年份与另一条差得远就阻止合并（范滂一条记 158-166、
       另一条记 137-169，实际是同一人）。
    """
    if not (a.get("biography") or "").strip() or not (b.get("biography") or "").strip():
        return True

    ab, ad = a.get("birthYear"), a.get("deathYear")
    bb, bd = b.get("birthYear"), b.get("deathYear")

    def close(x, y):
        if x is None or y is None:
            return True
        if abs(x - y) <= YEAR_TOLERANCE:
            return True
        # 符号写反的容错
        if (x > 0) != (y > 0) and abs(abs(x) - abs(y)) <= YEAR_TOLERANCE:
            return True
        return False

    return close(ab, bb) and close(ad, bd)


def richness(f):
    return (len(f.get("biography") or ""), len(f.get("summary") or ""),
            len(f.get("relatedEvents") or []) + len(f.get("relatedFigures") or []))


def merge_group(items):
    """返回 (保留者, 被合并的 id 列表)。"""
    items = sorted(items, key=richness, reverse=True)
    keep = dict(items[0])
    dropped = []

    for donor in items[1:]:
        dropped.append(donor["id"])
        # 字符串字段：保留者缺失时补
        for field in ("biography", "summary", "role", "alias", "lifeText",
                      "territory", "culture", "gender"):
            if not (keep.get(field) or "").strip() and (donor.get(field) or "").strip():
                keep[field] = donor[field]
        # 生卒年互补
        for field in ("birthYear", "deathYear"):
            if keep.get(field) is None and donor.get(field) is not None:
                keep[field] = donor[field]
        # 列表字段取并集
        for field in LIST_FIELDS:
            merged = list(keep.get(field) or [])
            for x in donor.get(field) or []:
                if x not in merged:
                    merged.append(x)
            if merged:
                keep[field] = merged

    return keep, dropped


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        figs = d.get("figures") or []

        groups = collections.defaultdict(list)
        for f in figs:
            n = (f.get("name") or "").strip()
            if n:
                groups[n].append(f)

        rename = {}
        survivors = {}
        skipped = []
        merged_groups = 0

        for name, items in groups.items():
            if len(items) < 2:
                continue
            # 显式合并优先：整组视为同一人
            if name in FORCE_MERGE:
                keep, dropped = merge_group(items)
                by, dy = FORCE_MERGE[name]
                keep["birthYear"], keep["deathYear"] = by, dy
                if by is not None and dy is not None:
                    def _fmt(y):
                        return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)
                    keep["lifeText"] = f"{_fmt(by)}－{_fmt(dy)}"
                survivors[keep["id"]] = keep
                for did in dropped:
                    rename[did] = keep["id"]
                merged_groups += 1
                continue
            # 只有彼此生卒年都兼容的才归为一组
            clusters = []
            for item in items:
                placed = False
                for cl in clusters:
                    if all(year_compatible(item, x) for x in cl):
                        cl.append(item)
                        placed = True
                        break
                if not placed:
                    clusters.append([item])
            for cl in clusters:
                if len(cl) < 2:
                    continue
                keep, dropped = merge_group(cl)
                if not dropped:
                    continue
                survivors[keep["id"]] = keep
                for did in dropped:
                    rename[did] = keep["id"]
                merged_groups += 1
            if len(clusters) > 1:
                skipped.append((name, [len(c) for c in clusters]))

        if not survivors:
            print(f"{path}: no duplicates merged")
            continue

        # 重建人物列表
        new_figs = []
        by_id = {}
        for f in figs:
            if f["id"] in rename:
                continue                      # 副本丢弃
            by_id[f["id"]] = f if f["id"] not in survivors else survivors[f["id"]]
            new_figs.append(f if f["id"] not in survivors else survivors[f["id"]])

        d["figures"] = new_figs

        # 改写引用（必须在 d["figures"] 指向新列表之后，
        # 否则保留者自身的 relatedFigures 不会被改写）
        for kind in ("periods", "events", "figures"):
            for item in d.get(kind) or []:
                for field in ("keyFigures", "figures", "relatedFigures"):
                    vals = item.get(field)
                    if not vals:
                        continue
                    out = []
                    for v in vals:
                        nv = rename.get(v, v)
                        if nv not in out:
                            out.append(nv)
                    item[field] = out

        # 名字与内容不符的条目单独修正
        fixed_names = 0
        for f in new_figs:
            spec = NAME_FIX.get(f["id"])
            if not spec:
                continue
            nm, by, dy = spec
            f["name"] = nm
            f["birthYear"], f["deathYear"] = by, dy

            def _fmt(y):
                return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)

            if by is not None and dy is not None:
                f["lifeText"] = f"{_fmt(by)}－{_fmt(dy)}"
            # 传记首句以旧名开头时替换为新名
            bio = f.get("biography") or ""
            if bio:
                head, sep, tail = bio.partition("是")
                if head and len(head) <= 4:
                    f["biography"] = nm + sep + tail
            fixed_names += 1
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))

        print(f"{path}: 合并 {merged_groups} 组，删除 {len(rename)} 条副本，"
              f"人物 {len(figs)} -> {len(new_figs)}，改名 {fixed_names} 条")
        if skipped:
            print(f"  同名但生卒年不兼容、未合并的分组: {len(skipped)}")
            for n, sizes in skipped[:10]:
                print(f"    {n} 分属 {len(sizes)} 个不同人物")


if __name__ == "__main__":
    main()
