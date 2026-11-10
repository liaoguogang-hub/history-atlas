import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 中英夹杂的常见误译 → 正确中文
REPLACEMENTS = [
    ("整顿吏治 economy 与", "整顿吏治经济与"),
    ("整顿吏治 economy、", "整顿吏治经济、"),
    ("economy 与安史之乱前", "经济与安史之乱前"),
    ("经济 economy", "经济"),
    ("政治 politics", "政治"),
    ("军事 military", "军事"),
    ("文化 culture", "文化"),
    ("科技 science", "科技"),
    ("宗教 religion", "宗教"),
    ("社会 society", "社会"),
    ("艺术 art", "艺术"),
    ("文学 literature", "文学"),
    ("教育 education", "教育"),
    ("探索 exploration", "探索"),
    ("改革 reform", "改革"),
    ("条约 treaty", "条约"),
    ("战争 conflict", "战争"),
    ("王朝 dynasty", "王朝"),
    ("跨文明交流 cross", "跨文明交流"),
    ("传说 legend", "传说"),
    ("考古 archaeology", "考古"),
    ("经济危机 economy", "经济危机"),
]

# detail / summary 里常见的整句英文残留 → 中文（按需扩充）
SENTENCE_FIX = {
    "线性B": "线性B",     # 保留：这是国际通用的考古学称名
}


def clean(text):
    if not text:
        return text
    out = text
    for a, b in REPLACEMENTS:
        out = out.replace(a, b)
    return out


def main():
    total = 0
    for sc in ["china", "world"]:
        p = f"data/{sc}.json"
        d = json.load(io.open(p, encoding="utf-8"))
        n = 0
        for e in d.get("events") or []:
            for field in ("summary", "detail"):
                v = e.get(field)
                if isinstance(v, str) and v:
                    nv = clean(v)
                    if nv != v:
                        e[field] = nv
                        n += 1
        for f in d.get("figures") or []:
            for field in ("summary", "biography"):
                v = f.get(field)
                if isinstance(v, str) and v:
                    nv = clean(v)
                    if nv != v:
                        f[field] = nv
                        n += 1
        io.open(p, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{sc}: cleaned {n} fields")
        total += n
    print("total:", total)


if __name__ == "__main__":
    main()
