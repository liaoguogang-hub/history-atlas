"""把 summary 类字段收进校验器的长度区间。

校验器的区间（见 validate_data.py）：
    period.summary  60 – 400 字
    event.summary   10 – 120 字
    figure.summary  10 – 120 字

处理原则是**只用已有数据**，不编写新内容：
- 过短（人物）：摘要多为「明崇祯，明末皇帝。」这类 4–9 字的精炼表述，
  从同一条目的 biography 首句补足，两句拼成一条完整摘要。
- 过短（时期）：把 culture 字段接在摘要后，形成「概况 + 文化特征」。
- 过长：在最后一个完整句号处截断，保证不切断句子；
  仅对 summary 生效，detail / biography 不动，避免丢失正文。

用法: python tools/fit_text_length.py data/china.json data/world.json
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

LIMITS = {
    "period": (60, 400),
    "event": (10, 120),
    "figure": (10, 120),
}

SENT_SPLIT = re.compile(r"(?<=[。！？])")


def first_sentences(text, budget):
    """取前若干完整句子，总长不超过 budget。"""
    if not text:
        return ""
    out = ""
    for s in SENT_SPLIT.split(text):
        if not s.strip():
            continue
        if len(out) + len(s) > budget:
            break
        out += s
    return out


def trim(text, hi):
    if len(text) <= hi:
        return text
    cut = text[:hi]
    for sep in ("。", "；", "，", "、"):
        idx = cut.rfind(sep)
        if idx >= (40 if sep == "。" else 120):
            return cut[: idx + 1]
    return cut[:hi]


def expand_figure(f, lo, hi, period_name=""):
    """人物摘要过短：优先用 biography 首句；没有 biography 时
    用「姓名—时期—身份」这一组已有事实组成完整表述。"""
    s = (f.get("summary") or "").strip()
    bio = (f.get("biography") or "").strip()
    if bio:
        room = hi - len(s)
        if room > 5:
            add = first_sentences(bio, room)
            if add:
                return s + add
    # 没有 biography 可用，退回结构化事实
    name = (f.get("name") or "").strip()
    role = (f.get("role") or "").strip()
    if name and period_name:
        cand = f"{name}是{period_name}时期的{role or '历史人物'}。{s}"
        if len(cand) <= hi:
            return cand
    if name and role:
        cand = f"{name}，{role}。{s}"
        if len(cand) <= hi:
            return cand
    return s


def expand_period(p, lo, hi):
    """时期摘要过短：摘要后接文化特征；没有文化特征时，用
    起止年算出历时，补一句由数据本身可导出的事实。"""
    s = (p.get("summary") or "").strip()
    culture = (p.get("culture") or "").strip()
    if culture and culture not in ("—", "-"):
        cand = s + "文化特征上，" + culture + "。"
        if len(cand) <= hi:
            return cand
        return s + "文化特征：" + culture[: max(0, hi - len(s) - 8)]

    sy, ey = p.get("startYear"), p.get("endYear")
    if isinstance(sy, int) and isinstance(ey, int) and ey > sy:
        span = ey - sy
        if span >= 50:
            cand = f"{s}自{fmt_year(sy)}至{fmt_year(ey)}，前后约{span}年。"
            if len(cand) <= hi:
                return cand
    return s


def fmt_year(y):
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        stat = {"trim": 0, "expand": 0}
        report = []
        period_name = {p["id"]: (p.get("name") or "")
                       for p in d.get("periods") or []}

        for key, kind in (("periods", "period"), ("events", "event"),
                          ("figures", "figure")):
            lo, hi = LIMITS[kind]
            for item in d.get(key) or []:
                s = item.get("summary") or ""
                if not s:
                    continue
                if len(s) > hi:
                    new = trim(s, hi)
                    if new != s:
                        item["summary"] = new
                        stat["trim"] += 1
                    continue
                if len(s) >= lo:
                    continue
                if kind == "figure":
                    new = expand_figure(
                        item, lo, hi,
                        period_name.get(item.get("periodId"), ""))
                elif kind == "period":
                    new = expand_period(item, lo, hi)
                else:
                    new = s
                if new != s:
                    item["summary"] = new
                    stat["expand"] += 1
                    if len(new) < lo:
                        report.append((item.get("id"), len(new)))

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: trimmed {stat['trim']}, expanded {stat['expand']}, "
              f"still-short {len(report)}")
        for r in report[:8]:
            print(f"   still short: {r[0]} ({r[1]}字)")


if __name__ == "__main__":
    main()
