"""扩充人物内容前的准备工作。

做三件事：
1. 列出待扩充人物（生平过短、缺成就或缺关联），按时期分组输出清单，
   便于分批撰写内容。
2. 检查同 id / 同名的人物是否分散在不同分片里，列出可能重复的条目。
3. 检查人物 id 与实际姓名是否吻合——历史项目里常见的问题是
   把某个 id 错配给了另一个人（例如某条 id 叫「lu-xun」但内容实为鲁迅），
   这类错误在扩充内容时必须先发现，否则会把错误固化。
"""
import io
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

# 一些 id 里带的名字片段与实际人名明显不符的条目。
# 这些是历史遗留的 id 错配，扩充前需要人工确认。
SUSPECT_ID_TOKENS = {
    "lu-xun": "周树人（鲁迅）而非陆逊",
    "zhu-di": "朱棣（明成祖）而非朱载堃",
    "zhu-yougui": "朱友珪而非朱由桂",
    "zhu-zhou": "朱厚熜（嘉靖）",
    "taichang": "朱常洛（泰昌帝）",
    "longqing": "朱载堃（隆庆帝）",
    "jiaqing": "永琰（嘉庆帝）",
    "chengjisihan": "成吉思汗",
    "ogodei": "窝阔台",
    "lirenzhong": "李仁孝",
    "liwang-yan": "李嗣源",
}


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    periods = {p["id"]: p for p in d["periods"]}
    figs = d["figures"]

    # ---- 1. 按时期分组的待扩充清单 ----
    by_period = defaultdict(list)
    for f in figs:
        bio = len(f.get("biography") or "")
        ach = len(f.get("achievements") or [])
        if bio < 260 or ach == 0:
            p = periods.get(f.get("periodId"))
            pname = p.get("name") if p else "?"
            by_period[pname].append((f["id"], f.get("name"), bio, ach))

    total = sum(len(v) for v in by_period.values())
    print(f"=== {path} 待扩充 {total} 人（生平<260字 或 无成就） ===")
    for pname, items in sorted(by_period.items(), key=lambda kv: -len(kv[1])):
        print(f"\n-- {pname}（{len(items)} 人）--")
        for fid, name, bio, ach in items:
            print(f"   {fid:26s} {name:10s} {bio:3d}字 ach={ach}")

    # ---- 2. 同名条目（不同 id 但同一人物）----
    by_name = defaultdict(list)
    for f in figs:
        by_name[f.get("name")].append(f["id"])
    dup = {k: v for k, v in by_name.items() if len(v) > 1}
    if dup:
        print(f"\n=== 同名多 id（可能是同一人被拆开）: {len(dup)} 组 ===")
        for k, v in list(dup.items())[:20]:
            print(f"   {k}: {v}")

    # ---- 3. id 与姓名不符的可疑条目 ----
    suspects = []
    for f in figs:
        for token, note in SUSPECT_ID_TOKENS.items():
            if token in f["id"]:
                suspects.append((f["id"], f.get("name"), note))
                break
    if suspects:
        print(f"\n=== id 与姓名可能错配: {len(suspects)} 条 ===")
        for fid, name, note in suspects:
            print(f"   {fid:26s} 实际姓名={name:8s}  疑点: {note}")


if __name__ == "__main__":
    main()
