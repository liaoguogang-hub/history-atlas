# -*- coding: utf-8 -*-
"""Unified repair pipeline for JSON shards, applied in the correct order and
saving after each successful step:
  1. convert_inner_quotes  (ASCII " inside string values -> full-width)
  2. balance_fullwidth     (U+201D runs -> paired U+201C/U+201D)
  3. fix_figures_orphans   ("figures":[],"fig-x"] -> "figures":["fig-x"])
  4. strip_bad_escapes     (invalid \\X -> X)
  5. parse & normalize     (write compact json)
Each step is applied to the whole text; we retry after each step until stable.
"""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
RD = "\u201d"
LD = "\u201c"


def convert_inner_quotes(text):
    out = []
    i = 0
    n = len(text)
    in_str = False
    inner = 0
    while i < n:
        c = text[i]
        if c == '"':
            if not in_str:
                in_str = True
                out.append('"')
            else:
                j = i + 1
                while j < n and text[j] in " \t":
                    j += 1
                nxt = text[j] if j < n else ""
                if nxt in ",}]:":
                    in_str = False
                    out.append('"')
                else:
                    out.append(LD if inner % 2 == 0 else RD)
                    inner += 1
            i += 1
            continue
        if c == "\n":
            in_str = False
            inner = 0
        out.append(c)
        i += 1
    return "".join(out)


def balance(text):
    def fixrun(mm):
        cnt = len(mm.group(0))
        return "".join((LD if k % 2 == 0 else RD) for k in range(cnt))
    return re.sub(RD + "+", fixrun, text)


def fix_figures(text):
    def rep(m):
        ids = re.findall(r'"(fig-[^"]*)"', m.group(1))
        return '"figures":[' + ",".join('"%s"' % i for i in ids) + "]"
    text = re.sub(r'"figures":\[\],((?:"fig-[^"]*"\s*,?\s*)+)\]', rep, text)
    text = re.sub(r'"figures":\[\],"(fig-[^"]*)"\]', r'"figures":["\1"]', text)
    return text


def strip_escapes(text):
    return re.sub(r"\\(?=[A-Za-z])", "", text)


def process(fname):
    path = os.path.join(TMP, fname)
    text = io.open(path, encoding="utf-8").read()
    for attempt in range(12):
        before = text
        text = convert_inner_quotes(text)
        text = balance(text)
        text = fix_figures(text)
        text = strip_escapes(text)
        try:
            d = json.loads(text)
            io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
            print(fname, "OK ->", len(d), "entries (pass %d)" % (attempt + 1))
            return True
        except Exception as e:
            if text == before:
                print(fname, "FAILED:", e)
                for i, LL in enumerate(text.split("\n"), 1):
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
                return False
    print(fname, "gave up")
    return False


if __name__ == "__main__":
    ok = True
    for f in sys.argv[1:]:
        if not process(f):
            ok = False
    sys.exit(0 if ok else 1)
