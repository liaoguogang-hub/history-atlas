import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
raw = io.open(path, encoding="utf-8").read()

# 0. auto-fix common invalid literals
import re as _re

# 精确修复："by"/"dy" 的值是不合法的 ? 占位符
_bd_pat = _re.compile(r'"(by|dy)":\s*"\?"|"(by|dy)":\s*-\?(?=[,\s}])')
raw, _n = _bd_pat.subn(lambda m: f'"{m.group(1) or m.group(2)}":null', raw)
if _n:
    print(f"auto-fix invalid ? placeholders in by/dy: x{_n}")
    io.open(path, "w", encoding="utf-8").write(raw)

# 1. control chars
ctrl = [i for i, l in enumerate(raw.split("\n"), 1)
        if any(ord(c) < 32 and c != "\t" for c in l)]
if ctrl:
    print("CONTROL CHARS on lines:", ctrl[:10])

# 2. try parse
try:
    arr = json.loads(raw)
    print("PARSE OK:", len(arr), "records")
except Exception as e:
    print("PARSE FAIL:", e)
    # locate the offending line
    m = re.search(r"line (\d+) column (\d+)", str(e))
    if m:
        ln = int(m.group(1))
        lines = raw.split("\n")
        for i in range(max(0, ln - 2), min(len(lines), ln + 1)):
            print(f"  {i+1}: {lines[i][:250]!r}")
    sys.exit(1)

ids = [r.get("id") for r in arr]
dup = [i for i in set(ids) if ids.count(i) > 1]
print("dup ids:", dup)

# 3. check no stray ASCII quotes inside values (would already have broken parsing)
# 4. check required fields
required = ["id", "n", "p", "lt", "ro", "s", "bio"]
bad = []
for r in arr:
    for f in required:
        if not r.get(f):
            bad.append((r.get("id"), f))
print("records missing required fields:", len(bad))
for b in bad[:8]:
    print("   ", b)

# 5. check year ordering
# 负数年份表示公元前，数值越小时间越早，因此统一用 by <= dy 判断。
for r in arr:
    by, dy = r.get("by"), r.get("dy")
    if not isinstance(by, int) or not isinstance(dy, int):
        continue
    if by > dy:
        print("  BAD YEAR ORDER:", r["id"], by, dy)

print("period ids used:", sorted({r.get("p") for r in arr}))
