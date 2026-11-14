# -*- coding: utf-8 -*-
"""v2.6.0 批次1：修正中国当代人物归期 + 补缺失卒年。

问题一：当代领导人归期错乱
  胡锦涛(1942-)、温家宝(1942-) 被归到 cn-modern-anti-japan（抗日战争 1931-1945）
  —— 他们出生时抗战尚未结束，但政治生涯在 2003-2013 年。
  习近平(1953-)、王毅(1955-) 被归到 cn-prc-early（1949-1978），
  实际属于 cn-prc-new-era（2012-2026）。
  「新时代」时期 0 人物。

问题二：24 人缺 deathYear
  其中很多是史书有明确卒年的历史人物（康熙 1722、乾隆 1799、
  霍去病 -117、张良 -186、萧何 -193 等），以及已故的当代人物
  （朱德 1976、叶剑英 1986、贺龙 1969、李大钊 1927）。
  缺卒年会导致「生卒年相同」被误判为同一人，也影响时代审计。

修复：
  1) 补齐可考证的 deathYear
  2) 修正当代人物 periodId
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 人物 id 或姓名关键词 : 补全的 deathYear
DEATH_FILL = {
    # 清代
    "康熙": 1722, "乾隆": 1799, "慈禧": 1908, "光绪": 1908,
    "建文帝": 1402, "方孝孺": 1402, "张献忠": 1647,
    # 秦汉
    "张良": -186, "萧何": -193, "范增": -204, "霍去病": -117,
    # 明清之际
    "马可·波罗": 1324, "利玛窦": 1610,
    # 已故当代人物
    "朱德": 1976, "叶剑英": 1986, "贺龙": 1969, "叶挺": 1946,
    "李大钊": 1927,
}

# 姓名关键词 : 新 periodId
PERIOD_FIX = {
    "胡锦涛": "cn-prc-reform",      # 2003-2013 执政，属改革开放时期
    "温家宝": "cn-prc-reform",      # 2003-2013 任总理
    "习近平": "cn-prc-new-era",     # 2012 至今
    "王毅": "cn-prc-new-era",       # 2013 至今任外长
    "李克强": "cn-prc-new-era",     # 2013-2023 任总理
}


def main():
    dry = "--dry-run" in sys.argv

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    pm = {p["id"]: p for p in china["periods"]}

    death_by_id = {}
    period_by_id = {}
    for f in china["figures"]:
        name = f.get("name") or ""
        for key, year in DEATH_FILL.items():
            if key in name and f.get("deathYear") is None:
                death_by_id[f["id"]] = year
                print("  卒年 %-12s → %s" % (name, year))
                break
        for key, pid in PERIOD_FIX.items():
            if key in name and pid in pm:
                if f.get("periodId") != pid:
                    period_by_id[f["id"]] = pid
                    print("  归期 %-12s %s → %s" % (name, f.get("periodId"), pid))
                break

    if not death_by_id and not period_by_id:
        print("无需改动。")
        return

    # 补丁分片
    patterns = ["figdata_*.json", "china_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    patched = 0
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
            rid = rec.get("id")
            if rid in death_by_id:
                key = "d" if ("d" in rec and "deathYear" not in rec) else "deathYear"
                if rec.get(key) is None:
                    rec[key] = death_by_id[rid]
                    patched += 1
                    changed = True
            if rid in period_by_id:
                key = "p" if ("p" in rec and "periodId" not in rec) else "periodId"
                if rec.get(key) != period_by_id[rid]:
                    rec[key] = period_by_id[rid]
                    patched += 1
                    changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print("\n补丁 %d 处。" % patched)
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
