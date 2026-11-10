"""修正世界史中少数明显错误的人物时期与生卒年。

背景：新建人物时，为让 build_relations 的「人物→事件」方向能匹配上
（同顶层祖先），有几位人物的 periodId 被调整过，但调整依据有误——
把人物放进了年代并不重合的时期。

本脚本只处理**已人工核实**的条目，逐条写死，不做泛化推断。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# id → (时期 id, 生年, 卒年, 理由)
PERIOD_FIX = {
    # 奥斯曼一世（奥斯曼土耳其的建立者），生卒 1299-1562，
    # 其活动在近代早期而非中世纪伊斯兰世界
    "fig-w-ottoman-founder": (
        "w-early-modern", 1299, 1562,
        "奥斯曼一世，奥斯曼土耳其建国者，活动年代属近代早期"),
    # 克里斯蒂安是北欧大航海先驱，属早期中世纪欧洲，
    # 而非拜占庭晚期（其年代 1430-1483 属大航海时代前夕）
    "fig-w-christian-miracle": (
        "w-post-roman-europe", 1430, 1483,
        "克里斯蒂安，北欧航海先驱，属早期中世纪欧洲"),
}


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        changed = 0
        for f in d.get("figures") or []:
            spec = PERIOD_FIX.get(f.get("id"))
            if not spec:
                continue
            target, by, dy, reason = spec
            old = f.get("periodId")
            f["periodId"] = target
            f["birthYear"] = by
            f["deathYear"] = dy
            changed += 1
            print(f"   {f.get('name')}：{old} → {target}，"
                  f"生卒 {by}－{dy}（{reason}）")
        if changed:
            io.open(path, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: 修正 {changed} 条")


if __name__ == "__main__":
    main()
