#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并历史图鉴数据分片为最终 JSON。

兼容两种键名：
  缩写键  id/n/y/ye/p/c/loc/imp/s/d/f/t
  完整键  id/name/year/yearEnd/periodId/category/location/importance/summary/detail/figures/tags

用法:
    python tools/merge_shards.py --scope china --out data/china.json data/.tmp/china_p*.json
    python tools/merge_shards.py --scope china --out data/china.json data/.tmp/evdata_*.json data/.tmp/figdata_*.json
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def norm_period(d):
    return {
        "id": d["id"],
        "name": d.get("name") or d.get("n", ""),
        "alias": d.get("alias", ""),
        "parentId": d.get("parentId") if d.get("parentId") is not None else d.get("p"),
        "startYear": d.get("startYear", d.get("sy", 0)),
        "endYear": d.get("endYear", d.get("ey", 0)),
        "startDateText": d.get("startDateText", ""),
        "endDateText": d.get("endDateText", ""),
        "colorKey": d.get("colorKey", d.get("ck", "")),
        "summary": d.get("summary", d.get("s", "")),
        "territory": d.get("territory", d.get("terr", "")),
        "capital": d.get("capital", d.get("cap", "")),
        "population": d.get("population", d.get("pop", "")),
        "culture": d.get("culture", d.get("cult", "")),
        "keyFigures": d.get("keyFigures", d.get("kf", [])) or [],
        "relatedEvents": d.get("relatedEvents", d.get("re", [])) or [],
        "tags": d.get("tags", d.get("t", [])) or [],
    }


def norm_event(d):
    return {
        "id": d["id"],
        "name": d.get("name") or d.get("n", ""),
        "year": d.get("year", d.get("y", 0)),
        "yearEnd": d.get("yearEnd", d.get("ye")),
        "dateText": d.get("dateText", d.get("dt", "")),
        "periodId": d.get("periodId") or d.get("p", ""),
        "category": d.get("category") or d.get("c", ""),
        "location": d.get("location", d.get("loc", "")),
        "summary": d.get("summary", d.get("s", "")),
        "detail": d.get("detail", d.get("d", "")),
        "importance": d.get("importance", d.get("imp", 0)),
        "figures": d.get("figures", d.get("f", [])) or [],
        "tags": d.get("tags", d.get("t", [])) or [],
    }


def norm_figure(d):
    return {
        "id": d["id"],
        "name": d.get("name") or d.get("n", ""),
        "alias": d.get("alias", d.get("al", "")),
        "birthYear": d.get("birthYear", d.get("by")),
        "deathYear": d.get("deathYear", d.get("dy")),
        "lifeText": d.get("lifeText", d.get("lt", "")),
        "role": d.get("role", d.get("ro", "")),
        "periodId": d.get("periodId") or d.get("p", ""),
        "gender": d.get("gender", d.get("g", "")),
        "summary": d.get("summary", d.get("s", "")),
        "biography": d.get("biography", d.get("bio", d.get("b", ""))),
        "achievements": d.get("achievements", d.get("ac", [])) or [],
        "quotes": d.get("quotes", d.get("q", [])) or [],
        "relatedEvents": d.get("relatedEvents", d.get("re", [])) or [],
        "relatedFigures": d.get("relatedFigures", d.get("rf", [])) or [],
        "tags": d.get("tags", d.get("t", [])) or [],
    }


NORMALIZERS = {
    "periods": ("period", norm_period),
    "events": ("event", norm_event),
    "figures": ("figure", norm_figure),
}


def classify(item):
    """Guess the entity type of a raw dict by its distinguishing keys.

    判定依据必须是**类型专属字段**，不能用 `p` / `s` 这类通用缩写
    —— 事件的 periodId 缩写也是 `p`，summary 缩写也是 `s`。
    """
    # 时期：必有起止年份（startYear/sy + endYear/ey）
    if ("startYear" in item or "sy" in item) and ("endYear" in item or "ey" in item):
        return "periods"
    # 人物：必有生年/卒年或身份
    if ("birthYear" in item or "by" in item or "deathYear" in item
            or "dy" in item or "role" in item or "ro" in item):
        return "figures"
    # 事件：必有发生年
    if "year" in item or "y" in item:
        return "events"
    # 兜底：看有没有 endYear
    if "endYear" in item or "ey" in item:
        return "periods"
    return "events"


def year_text(y):
    """按契约 §2 生成展示文本：公元前为负数，公元后为正数。"""
    if y is None:
        return ""
    return f"公元前{-y}年" if y < 0 else f"公元{y}年"


def backfill_dates(dataset):
    """补全缺失的展示日期字段。

    数据方常只提供数值年份而省略展示字段，导致 App 事件列表的日期列显示为「—」。
    这里按契约的「数值 + 展示文本双轨制」自动补齐。
    """
    for e in dataset["events"]:
        if not (e.get("dateText") or "").strip():
            e["dateText"] = year_text(e.get("year"))
        ye, y = e.get("yearEnd"), e.get("year")
        if ye is not None and y is not None and ye != y:
            e["dateText"] = f"{year_text(y)}－{year_text(ye)}"

    for p in dataset["periods"]:
        if not (p.get("startDateText") or "").strip():
            p["startDateText"] = year_text(p.get("startYear"))
        if not (p.get("endDateText") or "").strip():
            p["endDateText"] = year_text(p.get("endYear"))

    for f in dataset["figures"]:
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
    return dataset


def sync_event_years(dataset):
    """用 dateText 校正事件 year / yearEnd 的符号与量级。

    dateText 是人写的、语义明确（「公元前20万年－公元前50万年」），而数值字段
    常被写成正数或写反。以文本为准可避免「yearEnd 早于 year」这类错误。
    """
    import re

    tok = re.compile(r"(公元前|公元)\s*([\d.]+)\s*(万)?\s*年")

    def parse(text):
        if not text:
            return None
        toks = tok.findall(text)
        if len(toks) < 2:
            return None
        vals = []
        for pre, num, wan in toks[:2]:
            v = float(num)
            if wan:
                v *= 10000
            vals.append(-v if pre == "公元前" else v)
        return int(vals[0]), int(vals[1])

    for e in dataset["events"]:
        parsed = parse(e.get("dateText"))
        if not parsed:
            continue
        y, ye = parsed
        e["year"] = y
        if e.get("yearEnd") is not None:
            e["yearEnd"] = ye
    return dataset


def sync_years_from_life_text(dataset):
    """用 lifeText 校正 birthYear / deathYear。

    数据方常把公元年份误写成负数（负数=公元前），
    而 lifeText 是人写的、语义明确，因此以它为准。
    """
    import re

    tok = re.compile(r"(公元前|公元)\s*(\d+)\s*年")

    for f in dataset["figures"]:
        lt = f.get("lifeText") or ""
        toks = tok.findall(lt)
        if len(toks) < 2:
            continue
        (p1, n1), (p2, n2) = toks[0], toks[1]
        by = -int(n1) if p1 == "公元前" else int(n1)
        dy = -int(n2) if p2 == "公元前" else int(n2)
        if f.get("birthYear") != by or f.get("deathYear") != dy:
            f["birthYear"] = by
            f["deathYear"] = dy
    return dataset


def clean_english_residue(dataset):
    """清理中文内容里的英文残留。

    数据生成过程中偶尔出现「中文词被误译成英文」的残留（如 `厚待而.dim不使`）。
    这里只做**删除**与极少数确定的替换，绝不意译 —— 宁可少一个词，
    也不能造出「郑之防火墙」这种更糟的结果。
    """
    import re

    safe = [
        ("bronze", "青铜"), ("retired", "退居"), ("thousand", "千"),
        ("war", "战"), ("millet", "粟"), ("grain", "谷"),
        ("precursor", "前身"),
    ]
    latin = re.compile(r"[A-Za-z][A-Za-z\-']{1,}")

    def scrub(text):
        if not isinstance(text, str) or not text:
            return text
        for en, zh in safe:
            text = text.replace(en, zh)
        text = latin.sub("", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"([，、；：])\s*\.", r"\1", text)
        text = re.sub(r"\.\s*([，。；：、])", r"\1", text)
        text = re.sub(r"[/\\]\s*", "", text)
        text = re.sub(r"([，。；：、！？])\s*[，。；：、]", r"\1", text)
        text = re.sub(r"，\s*。", "。", text)
        text = re.sub(r"。\s*，", "。", text)
        text = re.sub(r"，\s*；", "；", text)
        text = re.sub(r"；\s*，", "；", text)
        text = re.sub(r"\s+([，。；：、！？）」』])", r"\1", text)
        text = re.sub(r"([（「『])\s+", r"\1", text)
        text = re.sub(r"\s*,\s*", "，", text)
        text = re.sub(r"\s*;\s*", "；", text)
        text = re.sub(r"([，。；：、！？])\1+", r"\1", text)
        return re.sub(r"\s+", " ", text).strip()

    text_fields = {
        "events": ("name", "summary", "detail", "location"),
        "periods": ("name", "alias", "summary", "territory", "capital", "culture"),
        "figures": ("name", "alias", "summary", "biography"),
    }
    list_fields = ("tags", "achievements", "quotes")

    for kind, fields in text_fields.items():
        for item in dataset[kind]:
            for fld in fields:
                if isinstance(item.get(fld), str):
                    item[fld] = scrub(item[fld])
            for fld in list_fields:
                lst = item.get(fld)
                if isinstance(lst, list):
                    for i, v in enumerate(lst):
                        if isinstance(v, str):
                            lst[i] = scrub(v)
    return dataset


def _richness(rec):
    """衡量一条记录的完整度，用于同 id 去重时择优。

    以正文长度为第一权重，其次看摘要与关联数量。
    """
    bio = rec.get("biography") or rec.get("detail") or ""
    summ = rec.get("summary") or ""
    links = len(rec.get("relatedEvents") or []) + len(rec.get("relatedFigures") or []) \
        + len(rec.get("figures") or []) + len(rec.get("keyFigures") or [])
    return (len(bio), len(summ), links)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True, choices=["china", "world"])
    ap.add_argument("--out", required=True)
    ap.add_argument("shards", nargs="+")
    args = ap.parse_args()

    files = []
    for pat in args.shards:
        files.extend(sorted(glob.glob(pat)))
    if not files:
        print("no shard files matched", file=sys.stderr)
        return 2

    buckets = {"periods": [], "events": [], "figures": []}
    seen = {"periods": set(), "events": set(), "figures": set()}
    dup = 0

    for path in files:
        try:
            raw = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            # 分片里混入裸控制字符（换行/制表符未转义）时，尝试清洗后重试，
            # 避免因为一个坏字符丢掉整片数据。
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
                cleaned = "".join(
                    ch if ch >= " " or ch in "\n\r\t" else " "
                    for ch in text
                )
                raw = json.loads(cleaned)
                print(f"REPAIRED {os.path.basename(path)} (control chars)", file=sys.stderr)
            except Exception:
                print(f"SKIP {os.path.basename(path)}: {e}", file=sys.stderr)
                continue

        # A shard is either a list of entities, or a dict with the three keys.
        if isinstance(raw, dict):
            groups = {k: v for k, v in raw.items() if k in buckets}
            if not groups:
                groups = {"events": raw if isinstance(raw, list) else []}
        elif isinstance(raw, list):
            groups = {}
            for item in raw:
                if not isinstance(item, dict) or "id" not in item:
                    continue
                g = classify(item)
                groups.setdefault(g, []).append(item)
        else:
            continue

        for g, items in groups.items():
            if g not in buckets:
                continue
            kind, normalizer = NORMALIZERS[g]
            index = {r["id"]: i for i, r in enumerate(buckets[g])}
            for item in items:
                norm = normalizer(item)
                rid = norm["id"]
                if rid not in seen[g]:
                    seen[g].add(rid)
                    index[rid] = len(buckets[g])
                    buckets[g].append(norm)
                    continue

                # 同 id 重复：保留内容更丰富的那一条。
                # 早先的实现「先出现者胜」，导致后加的补充分片被静默丢弃，
                # 补写的内容无法覆盖原始占位条目。
                dup += 1
                old_i = index.get(rid)
                if old_i is None:
                    continue
                if _richness(norm) > _richness(buckets[g][old_i]):
                    buckets[g][old_i] = norm

    out = {
        "version": 1,
        "scope": args.scope,
        "periods": buckets["periods"],
        "events": buckets["events"],
        "figures": buckets["figures"],
    }
    out = backfill_dates(out)
    out = sync_event_years(out)
    out = sync_years_from_life_text(out)
    out = clean_english_residue(out)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"merged {len(files)} shard(s) -> {args.out}")
    print(f"  periods={len(out['periods'])} events={len(out['events'])} figures={len(out['figures'])} (dup skipped: {dup})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
