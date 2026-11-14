# -*- coding: utf-8 -*-
"""v2.6.0 批次2：从 lifeText 解析并回填缺失的 deathYear。

问题：24 个人物的 `deathYear` 为 None，但它们的 `lifeText` 字段里
**明确写着卒年**，例如：

  fig-zzbq3-zhangliang  张良    lifeText="约公元前250年—前186年"   deathYear=None
  fig-zzbq2-kangxi      康熙    lifeText="公元1654年—1722年，在位1661年—1722年"  deathYear=None
  fig-zzbq2-zhude       朱德    lifeText="公元1886年—1976年"      deathYear=None

说明某个流水线步骤把 deathYear 清空了（源分片里其实有值），
但 lifeText 保留了完整信息。这里从 lifeText 反向解析补回。

解析规则：
  「公元前N年」→ -N    「公元N年」→ N    「前N年」→ -N
  形如 "X年—Y年" 时，取破折号后的第一个年份作为卒年。

补回 deathYear 的价值：
  1) 时代审计（_audit_cn_kf.py）需要卒年判断人物活跃期
  2) 避免「生卒年相同」被误判为同一人
  3) App 的人物详情页可正确显示生卒
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 匹配「公元前250年」「公元1654年」「前186年」这类表述
YEAR_RE = re.compile(r"(公元前|公元|前)?\s*(\d{1,5})\s*年")


def parse_year(text):
    m = YEAR_RE.search(text or "")
    if not m:
        return None
    sign, num = m.group(1), int(m.group(2))
    if sign in ("公元前", "前"):
        return -num
    return num


def parse_death_from_life(life_text):
    """从 lifeText 取破折号后的第一个年份作为卒年。"""
    if not life_text:
        return None
    # 统一破折号
    t = life_text.replace("—", "-").replace("–", "-").replace("~", "-")
    if "-" not in t:
        return None
    after = t.split("-", 1)[1]
    # "—？" 或 "—?" 表示卒年不详，不能误取后面的"在位"年份
    if after.strip().startswith(("？", "?")):
        return None
    dy = parse_year(after)
    return dy


def main():
    dry = "--dry-run" in sys.argv

    china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))

    targets = {}
    for f in china["figures"]:
        if f.get("deathYear") is not None:
            continue
        dy = parse_death_from_life(f.get("lifeText"))
        if dy is None:
            continue
        by = f.get("birthYear")
        if isinstance(by, int) and dy < by:
            continue                       # 卒年早于生年，解析可能有误，跳过
        targets[f["id"]] = dy
        print("  %-14s %s~?  lifeText=%s  → deathYear=%s" % (
            f["name"], by, f.get("lifeText"), dy))

    if not targets:
        print("无可补全项。")
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
            if rid in targets and rec.get("deathYear") in (None, ""):
                key = "d" if ("d" in rec and "deathYear" not in rec) else "deathYear"
                rec[key] = targets[rid]
                patched += 1
                changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print("\n补丁 %d 处（%d 人）。" % (patched, len(targets)))
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
