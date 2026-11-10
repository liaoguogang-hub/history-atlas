# -*- coding: utf-8 -*-
"""Fix orphaned figure ids left by earlier repairs: "figures":[],"fig-x"] -> "figures":["fig-x"]"""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"


def fix_line(L):
    # "figures":[],"fig-a","fig-b"]  ->  "figures":["fig-a","fig-b"]
    m = re.search(r'"figures":\[\],((?:"fig-[^"]*"\s*,?\s*)+)\]', L)
    if m:
        ids = re.findall(r'"(fig-[^"]*)"', m.group(1))
        if ids:
            repl = '"figures":[' + ",".join('"%s"' % i for i in ids) + "]"
            L = L[:m.start()] + repl + L[m.end():]
    # also: "figures":[],"fig-a"]  (single, no array close)
    m2 = re.search(r'"figures":\[\],"(fig-[^"]*)"\]', L)
    if m2:
        L = L[:m2.start()] + '"figures":["%s"]' % m2.group(1) + L[m2.end():]
    return L


def process(fname):
    path = os.path.join(TMP, fname)
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    s = "\n".join(fix_line(L) for L in lines)
    try:
        d = json.loads(s)
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fname, "OK ->", len(d), "entries")
    except Exception as e:
        print(fname, "still broken:", e)
        for i, LL in enumerate(s.split("\n"), 1):
            t = LL.rstrip().rstrip(",")
            if not t.strip() or t in ("[", "]"):
                continue
            try:
                json.loads(t)
            except Exception as e2:
                m = re.search(r"column (\d+)", str(e2))
                c = int(m.group(1)) if m else 0
                print("  line", i, e2)
                print("   ctx:", repr(LL[max(0, c-130):c+130]))


if __name__ == "__main__":
    for f in sys.argv[1:]:
        process(f)
