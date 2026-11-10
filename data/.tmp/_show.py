import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read().split('\n')
pat = re.compile(sys.argv[2])
for i, l in enumerate(s):
    if pat.search(l):
        for m in pat.finditer(l):
            a = max(0, m.start() - 60)
            b = min(len(l), m.end() + 60)
            print(i + 1, repr(l[a:b]))
