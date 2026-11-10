import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 修复被误伤的 "by":null-780 形式，还原成 "by":-780
pat = re.compile(r'"(by|dy)":\s*null(?=-)')
total = 0
for path in sys.argv[1:]:
    s = io.open(path, encoding="utf-8").read()
    s2, n = pat.subn(lambda m: f'"{m.group(1)}":', s)
    if n:
        io.open(path, "w", encoding="utf-8").write(s2)
        print(f"{path}: restored {n} broken year values")
        total += n
print("total restored:", total)
