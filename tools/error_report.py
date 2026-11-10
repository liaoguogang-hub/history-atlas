import io
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
raw = io.open(path, encoding="utf-8").read()

# 复用 validate_data 的输出不便，这里直接分类统计错误类型
sys.path.insert(0, "tools")
import validate_data as V  # noqa: E402


class Cap:
    def __init__(self):
        self.errors = []
        self.warns = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def info(self, msg):
        pass


cap = Cap()
data = json.loads(raw)
try:
    V.validate(data, cap)
except TypeError:
    V.validate_data(data, cap)

def classify(msg):
    m = re.match(r"\[(\w+)\]\s+(.*)", msg)
    if not m:
        return ("other", msg[:60])
    kind, rest = m.group(1), m.group(2)
    if "引用不存在的人物" in rest:
        return ("missing_figure_ref", rest[:70])
    if "引用不存在的事件" in rest:
        return ("missing_event_ref", rest[:70])
    if "引用不存在的时期" in rest:
        return ("missing_period_ref", rest[:70])
    if "起始年" in rest or "晚于" in rest:
        return ("year_order", rest[:70])
    if "不在时期" in rest:
        return ("event_outside_period", rest[:70])
    if "category" in rest or "colorKey" in rest:
        return ("enum", rest[:70])
    if "必填" in rest or "缺少" in rest or "为空" in rest:
        return ("missing_field", rest[:70])
    return (kind.lower(), rest[:70])

ec = collections.Counter()
wc = collections.Counter()
samples = collections.defaultdict(list)

for m in cap.errors:
    k, s = classify(m)
    ec[k] += 1
    if len(samples[k]) < 3:
        samples[k].append(s)

for m in cap.warns:
    k, s = classify(m)
    wc[k] += 1

print(f"=== {path} ===")
print(f"ERROR {len(cap.errors)}  WARN {len(cap.warns)}")
print("\n-- 错误分类 --")
for k, n in ec.most_common():
    print(f"  {n:5d}  {k}")
    for s in samples[k]:
        print(f"          e.g. {s}")
print("\n-- 警告分类 --")
for k, n in wc.most_common(10):
    print(f"  {n:5d}  {k}")
