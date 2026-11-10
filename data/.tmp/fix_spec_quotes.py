# -*- coding: utf-8 -*-
"""Convert inner ASCII double quotes inside JSON string values to full-width,
then parse. Works on the multi-line spec files."""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
LD = "\u201c"
RD = "\u201d"


def fix_text(v):
    """Apply to a single JSON string token's inner content."""
    return v


def convert_line(L):
    """Convert inner ASCII quotes to full-width, respecting JSON structure."""
    out = []
    i = 0
    n = len(L)
    in_str = False
    inner = 0
    while i < n:
        c = L[i]
        if c == '"':
            if not in_str:
                in_str = True
                out.append('"')
            else:
                j = i + 1
                while j < n and L[j] in " \t":
                    j += 1
                nxt = L[j] if j < n else ""
                if nxt in ",}]:":
                    in_str = False
                    out.append('"')
                else:
                    out.append(LD if inner % 2 == 0 else RD)
                    inner += 1
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
        if st in ("", "[", "]") or st.startswith("{") or st.startswith("}"):
            # structural lines: convert inner quotes only within string values
            out.append(convert_line(L))
            continue
        try:
            json.loads(t)
            out.append(L)
        except Exception:
            out.append(convert_line(L))
    s = "\n".join(out)
    try:
        d = json.loads(s)
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
        print(fname, "OK ->", len(d))
        return True
    except Exception as e:
        print(fname, "FAIL:", e)
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
                print("   ctx:", repr(LL[max(0, c-140):c+140]))
        return False


if __name__ == "__main__":
    for f in sys.argv[1:]:
        process(f)
