#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为缺失 dateText / startDateText / endDateText 的记录自动补全展示日期。

数据方可能只提供数值年份（year / startYear / endYear）而省略展示字段。
本脚本按契约 §2 的「数值 + 展示文本双轨制」补齐展示字段：
    -221  →  公元前221年
      9  →  公元9年
    2026  →  公元2026年

同时把过长的展示文本压缩到合理长度（用于窄色块）：
    公元前300万年 → 前300万年
    公元2026年    → 2026年

用法:
    python tools\fix_dates.py data\china.json data\world.json
    python tools\fix_dates.py --in-place data\china.json
"""
import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def year_text(y: int) -> str:
    """按契约约定生成展示文本：公元前为负数，公元后为正数。"""
    if y is None:
        return ""
    if y < 0:
        return f"公元前{-y}年"
    return f"公元{y}年"


def compact(y: int) -> str:
    """紧凑形式，用于宽度受限的色块。"""
    if y is None:
        return ""
    if y < 0:
        return f"前{-y}"
    return str(y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--in-place", action="store_true",
                    help="直接改写原文件（默认输出到 <name>.fixed.json）")
    args = ap.parse_args()

    for path in args.files:
        data = json.load(io.open(path, encoding="utf-8"))
        n_date = n_start = n_end = 0

        for e in data.get("events", []):
            if not (e.get("dateText") or "").strip():
                y = e.get("year")
                if y is not None:
                    e["dateText"] = year_text(y)
                    n_date += 1
            # 跨年事件用起止年生成更精确的展示
            ye = e.get("yearEnd")
            y = e.get("year")
            if ye is not None and y is not None and ye != y:
                e["dateText"] = f"{year_text(y)}－{year_text(ye)}"

        for p in data.get("periods", []):
            if not (p.get("startDateText") or "").strip():
                sy = p.get("startYear")
                if sy is not None:
                    p["startDateText"] = year_text(sy)
                    n_start += 1
            if not (p.get("endDateText") or "").strip():
                ey = p.get("endYear")
                if ey is not None:
                    p["endDateText"] = year_text(ey)
                    n_end += 1

        for f in data.get("figures", []):
            if not (f.get("lifeText") or "").strip():
                by, dy = f.get("birthYear"), f.get("deathYear")
                if by is not None and dy is not None:
                    f["lifeText"] = f"{year_text(by)}－{year_text(dy)}"
                elif by is not None:
                    f["lifeText"] = f"{year_text(by)}－卒年不详"
                elif dy is not None:
                    f["lifeText"] = f"生年不详－{year_text(dy)}"
                else:
                    f["lifeText"] = "生卒不详"

        if args.in_place:
            out = path
        else:
            out = os.path.splitext(path)[0] + ".fixed.json"

        io.open(out, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=1)
        )
        print(f"{path} -> {out}: "
              f"event.dateText +{n_date}, period.start +{n_start}, period.end +{n_end}")


if __name__ == "__main__":
    main()
