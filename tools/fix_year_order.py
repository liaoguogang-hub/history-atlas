import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
data = json.load(io.open(path, encoding="utf-8"))

# 1) category 归一
CAT_FIX = {
    "diplomacy": "treaty", "politics": "political", "war": "military",
    "economy": "economic", "culture": "cultural", "science": "scientific",
    "religion": "religious", "technology": "technology",
    "exploration": "exploration", "art": "art", "literature": "literature",
    "education": "education", "conflict": "conflict", "treaty": "treaty",
    "reform": "reform", "dynasty": "dynasty", "disaster": "disaster",
    "health": "health", "economy-crisis": "economy-crisis",
    "legend": "legend", "archaeology": "archaeology",
    "political": "political", "military": "military", "scientific": "scientific",
    "social": "social", "religious": "religious", "cross-civilization": "cross-civilization",
}
n = 0
for e in data["events"]:
    c = e.get("category")
    if c in CAT_FIX and CAT_FIX[c] != c:
        e["category"] = CAT_FIX[c]
        n += 1

# 2) 事件 year / yearEnd 顺序：若 yearEnd 早于 year，交换或对齐
#    负数=公元前，数值小=更早，所以"yearEnd 不早于 year"即 yearEnd >= year。
#    跨公元（year<0<yearEnd）也合法。
m = 0
for e in data["events"]:
    y, ye = e.get("year"), e.get("yearEnd")
    if not isinstance(y, int) or not isinstance(ye, int):
        continue
    if y < 0 <= ye:
        continue  # 跨公元，合法
    if ye < y:
        # 说明写反了：交换
        e["year"], e["yearEnd"] = ye, y
        m += 1

# 3) 人物 birthYear / deathYear 顺序
#    规则：生年必须不晚于卒年。负数=公元前，数值小=更早，
#    故统一用数值比较 by <= dy（公元前 -520 生、-446 卒 满足）。
p = 0
for f in data["figures"]:
    by, dy = f.get("birthYear"), f.get("deathYear")
    if not isinstance(by, int) or not isinstance(dy, int):
        continue
    if by < 0 <= dy:
        continue  # 跨公元，合法
    if by > dy:
        f["birthYear"], f["deathYear"] = dy, by
        p += 1

io.open(path, "w", encoding="utf-8").write(
    json.dumps(data, ensure_ascii=False, indent=1))
print(f"{path}: category fixed {n}, event years swapped {m}, figure years swapped {p}")
