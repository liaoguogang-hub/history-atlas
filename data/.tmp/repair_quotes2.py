# -*- coding: utf-8 -*-
"""Repair event shard lines where inner quotes became U+201D on BOTH sides.

Strategy per line: the JSON structure uses ASCII " as delimiters. Any U+201D
that appears as a *pair* around a phrase should become  U+201C ... U+201D.
So: find runs of U+201D; if a run has even length, convert alternating
U+201D -> U+201C (open) / U+201D (close). Odd leftovers -> U+201C.
Then the line should parse.
"""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
RD = "\u201d"
LD = "\u201c"


def fix_line(L):
    # collapse runs of U+201D into balanced pairs
    out = []
    i = 0
    n = len(L)
    while i < n:
        if L[i] == RD:
            j = i
            while j < n and L[j] == RD:
                j += 1
            cnt = j - i
            # make pairs: open, close
            s = ""
            for k in range(cnt):
                s += (LD if k % 2 == 0 else RD)
            out.append(s)
            i = j
        else:
            out.append(L[i])
            i += 1
    return "".join(out)


def process(fname):
    path = os.path.join(TMP, fname)
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    out = [fix_line(L) for L in lines]
    s = "\n".join(out)
    try:
        d = json.loads(s)
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fname, "OK ->", len(d), "entries")
        return
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
