import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
p = "data/.tmp/rest_b.json"
s = io.open(p, encoding="utf-8").read()
fixes = [
    ("李怀光，丰王李Bot之子（一作父为左骁卫大将军李茂）",
     "李怀光，丰王之子（一作父为左骁卫大将军李茂），唐代将领"),
    ("部下韩游瑰、康 noninstruct等相继叛离", "部下韩游瑰等相继叛离"),
    ('"fig-li-zi-2"', '"fig-li-shangyin"'),
    ('"ev-tang-jingde-2"', '"ev-tang-jingde"'),
    ('"fig-li-wang-yan"', '"fig-li-chang-tang"'),
]
for a, b in fixes:
    if a not in s:
        print("MISS:", a[:55])
        continue
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
print("done")
