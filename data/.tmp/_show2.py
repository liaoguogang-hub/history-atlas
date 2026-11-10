import io, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read().split('\n')
pat = re.compile(sys.argv[2])
for i, l in enumerate(s):
    if pat.search(l):
        for m in pat.finditer(l):
            a = max(0, m.start() - 80)
            b = min(len(l), m.end() + 80)
            print(i + 1, repr(l[a:b]))
