import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
p = "data/.tmp/rest_a.json"
s = io.open(p, encoding="utf-8").read()
fixes = [
    ("其御车者蔡福、张 Protected 欲救之而不听", "其御车者蔡福、张 Protected 欲救之而不听"),
    ("张 Protected 欲救之而不听", "张青欲救之而不听"),
]
for a, b in fixes:
    if a not in s:
        print("MISS:", a[:55])
        continue
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
print("done")
