import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 修复手误导致的键名损坏，例如 "s："s":  →  "s":  以及类似的 "n："n" 形式
pat = re.compile(r'"([a-zA-Z]+)："(\1)"\s*:')
total = 0
for path in sys.argv[1:]:
    s = io.open(path, encoding="utf-8").read()
    s2, n = pat.subn(lambda m: f'"{m.group(1)}": ', s)
    if n:
        io.open(path, "w", encoding="utf-8").write(s2)
        print(f"{path}: fixed {n} malformed keys")
        total += n
print("total fixed:", total)
