import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 事件的 year / yearEnd 与 dateText 需保持符号一致。
# 规则：dateText 中出现「公元前N年」→ 该端点为负；「公元N年」→ 为正。
#
# 例：ev-pre-peking-man
#   year = -500000, yearEnd = -200000, dateText = 「公元前50万年－公元前20万年」
#   公元前年份数值小 = 早，所以 year(-500000) <= yearEnd(-200000)，符号其实是对的；
#   但若写作「公元前20万年－公元前50万年」则为逆序，需交换。

tok = re.compile(r"(公元前|公元)\s*([\d.]+)\s*(万)?\s*年")


def parse_years(text):
    """从日期文本解析 (year, yearEnd)，保持符号与量级。"""
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
    return (int(vals[0]), int(vals[1]))


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    is_dataset = isinstance(data, dict)
    arr = data.get("events") or [] if is_dataset else data
    fixed = []
    for e in arr:
        if not isinstance(e, dict):
            continue
        dt = e.get("dateText") or ""
        parsed = parse_years(dt)
        if not parsed:
            continue
        y, ye = parsed
        cur_y, cur_ye = e.get("year"), e.get("yearEnd")
        if cur_y != y or (cur_ye is not None and cur_ye != ye):
            e["year"] = y
            if cur_ye is not None:
                e["yearEnd"] = ye
            fixed.append((e.get("id"), cur_y, cur_ye, y, ye))
    if fixed:
        if is_dataset:
            data["events"] = arr
            out = data
        else:
            out = arr
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{path}: synced {len(fixed)} event year pairs")
    for f in fixed[:12]:
        print("   ", f)


if __name__ == "__main__":
    main()
