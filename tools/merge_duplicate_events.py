"""合并同名事件。

原始分片里同一事件被写成多条（九一八事变 3 条、郑和下西洋 2 条、
土木堡之变 2 条…），导致事件流里重复出现，也让时间轴出现重叠标记。

策略与人物去重一致：
- 按 name 聚类，保留内容最丰富的一条
- 合并 figures / relatedEvents / tags 等列表字段
- 把 periods 与 figures 中对副本的引用改写为保留者
"""
import io
import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

LIST_FIELDS = ("figures", "tags", "relatedEvents", "relatedFigures")


def richness(e):
    return (len(e.get("detail") or ""), len(e.get("summary") or ""),
            len(e.get("figures") or []))


def merge(items):
    items = sorted(items, key=richness, reverse=True)
    keep = dict(items[0])
    dropped = []
    for donor in items[1:]:
        dropped.append(donor["id"])
        for field in ("detail", "summary", "category", "importance", "location"):
            if keep.get(field) in (None, "", 0) and donor.get(field) not in (None, "", 0):
                keep[field] = donor[field]
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
        evs = d.get("events") or []

        groups = collections.defaultdict(list)
        for e in evs:
            n = (e.get("name") or "").strip()
            if n:
                groups[n].append(e)

        rename = {}
        survivors = {}
        merged_groups = 0
        for name, items in groups.items():
            if len(items) < 2:
                continue
            keep, dropped = merge(items)
            survivors[keep["id"]] = keep
            for did in dropped:
                rename[did] = keep["id"]
            merged_groups += 1

        if not survivors:
            print(f"{path}: 无重名事件")
            continue

        new_evs = []
        for e in evs:
            if e["id"] in rename:
                continue
            new_evs.append(survivors.get(e["id"], e))
        d["events"] = new_evs

        # 改写引用
        for kind in ("periods", "events", "figures"):
            for item in d.get(kind) or []:
                for field in ("relatedEvents",):
                    vals = item.get(field)
                    if not vals:
                        continue
                    out = []
                    for v in vals:
                        nv = rename.get(v, v)
                        if nv not in out:
                            out.append(nv)
                    item[field] = out

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: 合并 {merged_groups} 组重名事件，"
              f"删除 {len(rename)} 条，事件 {len(evs)} -> {len(new_evs)}")


if __name__ == "__main__":
    main()
