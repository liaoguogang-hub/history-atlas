# -*- coding: utf-8 -*-
"""v2.1.0 批次13：修正 w-world-wars 中错挂的战后人物。

发现：w-world-wars(1914-1945) 下有 8 人，其中 6 人的主要成就远在 1945 年之后：
  巴兹·奥尔德林  1930-    1969 年登月          → w-tech-era
  尤里·加加林    1934-1968 1961 年首次载人航天  → w-tech-era
  詹姆斯·沃森    1928-    1953 年 DNA 双螺旋    → w-tech-era
  罗莎琳德·富兰克林 1920-1958 1952 年 X 射线衍射 → w-tech-era
  屠呦呦        1930-    1972 年发现青蒿素      → w-tech-era
  曼德拉        1918-2013 1994 年当选南非总统   → w-cold-war

他们的出生年确实落在 1914-1945，但历史地位来自战后成就，
挂在「两次世界大战」下会误导用户。归入 w-tech-era(1945-2026) 或 w-cold-war(1914-1990)。

保留在 w-world-wars 的：
  约翰·肯尼迪  1917-1963 — 二战服役，但主要身份是冷战总统 → 也应移入 w-cold-war
  加马尔·阿卜杜勒·纳赛尔 1918-1970 — 1952 年政变、1956 苏伊士 → w-cold-war

结论：w-world-wars 的 8 人全部应移出。该时期改为只保留真正属于 1914-1945 的人物
（如希特勒、罗斯福、丘吉尔、斯大林、列宁等，他们的 periodId 目前正确）。

★ 本脚本修改源分片 world_fig_*.json 的 periodId 字段。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

# 人物 id : 新 periodId
MOVE = {
    "fig-buzz-aldrin": "w-tech-era",
    "fig-yuri-gagarin": "w-tech-era",
    "fig-james-watson": "w-tech-era",
    "fig-rosalind-franklin": "w-tech-era",
    "fig-tu-youyou": "w-tech-era",
    "fig-mandela": "w-cold-war",
    "fig-john-f-kennedy": "w-cold-war",
    "fig-nasser": "w-cold-war",
}

# 兼容可能的其它 id 写法：按姓名兜底匹配
NAME_HINTS = {
    "奥尔德林": "w-tech-era",
    "加加林": "w-tech-era",
    "沃森": "w-tech-era",
    "罗莎琳德": "w-tech-era",
    "屠呦呦": "w-tech-era",
    "曼德拉": "w-cold-war",
    "肯尼迪": "w-cold-war",
    "纳赛尔": "w-cold-war",
}


def main():
    dry = "--dry-run" in sys.argv
    shards = sorted(glob.glob(os.path.join(HERE, "world_fig_*.json")))
    moved = 0
    touched = []

    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (obj.get("figures") or [])
        changed = False

        for rec in recs:
            if not isinstance(rec, dict):
                continue
            if rec.get("periodId") != "w-world-wars":
                continue
            rid = rec.get("id") or ""
            name = rec.get("name") or ""

            target = MOVE.get(rid)
            if not target:
                for hint, pid in NAME_HINTS.items():
                    if hint in name:
                        target = pid
                        break
            if not target:
                continue

            print(f"  ✓ {name} ({rid}): w-world-wars → {target}")
            rec["periodId"] = target
            moved += 1
            changed = True
            touched.append(os.path.basename(path))

        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print()
    print(f"共移动 {moved} 个人物（涉及 {len(set(touched))} 个分片）。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
