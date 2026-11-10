# -*- coding: utf-8 -*-
"""Single-pass correct repair for a JSON shard whose string values may contain
unescaped ASCII double quotes.

Algorithm per line:
  Walk the line; the JSON skeleton uses ASCII " at known key positions
  ("key": and separators). We detect structure by parsing with a state machine:
    - Outside a string: ASCII " starts a string.
    - Inside a string: ASCII " ends it ONLY if the next non-space char is one of
      , } ] :  AND the string content so far forms a valid value position.
      Otherwise it is an inner quote -> convert to U+201C / U+201D.
"""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"


def convert_inner_quotes(L):
    out = []
    i = 0
    n = len(L)
    in_str = False
    open_count = 0
    while i < n:
        c = L[i]
        if c == '"':
            if not in_str:
                in_str = True
                out.append('"')
            else:
                # look ahead for the closing context
                j = i + 1
                while j < n and L[j] in " \t":
                    j += 1
                nxt = L[j] if j < n else ""
                if nxt in ",}]:":
                    in_str = False
                    out.append('"')
                else:
                    # inner quote
                    if open_count % 2 == 0:
                        out.append("\u201c")
                    else:
                        out.append("\u201d")
                    open_count += 1
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def process(fname):
    path = os.path.join(TMP, fname)
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    out = []
    for L in lines:
        t = L.rstrip().rstrip(",")
        st = t.strip()
        if st in ("", "[", "]"):
            out.append(L)
            continue
        try:
            json.loads(t)
            out.append(L)
            continue
        except Exception:
            pass
        out.append(convert_inner_quotes(L))
    s = "\n".join(out)
    # also normalize U+201D-pairs back to balanced open/close
    def fixrun(mm):
        cnt = len(mm.group(0))
        return "".join(("\u201c" if k % 2 == 0 else "\u201d") for k in range(cnt))
    s = re.sub("\u201d+", fixrun, s)
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
