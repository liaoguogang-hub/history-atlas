# -*- coding: utf-8 -*-
"""Robust repair for event shards:
1. Fix `"figures":` followed by a non-array value -> `[]` (handles arrays correctly)
2. Remove invalid backslash escapes
3. Convert inner ASCII quotes to full-width marks (balanced per line)
"""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"


def repair_line(L):
    # 1) figures field: find '"figures":' then decide if next non-space char is '['
    out = []
    i = 0
    n = len(L)
    while i < n:
        m = re.compile(r'"figures":').search(L, i)
        if not m:
            out.append(L[i:])
            break
        out.append(L[i:m.start()])
        j = m.end()
        while j < n and L[j] in " \t":
            j += 1
        if j < n and L[j] == "[":
            # find matching ]
            depth = 0
            k = j
            while k < n:
                if L[k] == "[":
                    depth += 1
                elif L[k] == "]":
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
                k += 1
            out.append(L[m.start():k])
            i = k
        else:
            # non-array value: consume up to the next ',' or '}' at depth 0
            k = j
            while k < n and L[k] not in ",}":
                k += 1
            out.append('"figures":[]')
            i = k
    s = "".join(out)
    # 2) invalid backslash escapes
    s = re.sub(r"\\(?=[A-Za-z])", "", s)
    # 3) inner ASCII quotes -> full width, per line, quote-aware
    res = []
    inq = False
    j = 0
    m = len(s)
    while j < m:
        c = s[j]
        if c == '"':
            if inq:
                k = j + 1
                while k < m and s[k] in " \t":
                    k += 1
                if k < m and s[k] in ",}]:":
                    inq = False
                    res.append('"')
                else:
                    res.append("\u201d")
            else:
                inq = True
                res.append('"')
            j += 1
            continue
        res.append(c)
        j += 1
    s = "".join(res)
    # 4) repair smart-quote pairs that are unbalanced within the line
    return s


def process(fname):
    path = os.path.join(TMP, fname)
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    out = [repair_line(L) for L in lines]
    s = "\n".join(out)
    try:
        d = json.loads(s)
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fname, "OK ->", len(d), "entries")
    except Exception as e:
        print(fname, "STILL BROKEN:", e)
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
                print("   ctx:", repr(LL[max(0, c-120):c+120]))


if __name__ == "__main__":
    for f in sys.argv[1:]:
        process(f)
