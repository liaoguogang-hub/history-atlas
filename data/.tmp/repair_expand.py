# -*- coding: utf-8 -*-
"""Repair + validate expansion shards: fix JSON typos, then report Latin leaks."""
import io, json, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
LATIN = re.compile(r"[A-Za-z]{2,}")


def repair_line(L):
    # fix ""name": -> "name":
    L = L.replace('""name":', '"name":')
    # fix stray "": patterns
    L = re.sub(r'""(\w+)"\s*:', r'"\1":', L)
    return L


def load(fname):
    path = os.path.join(TMP, fname)
    raw = io.open(path, encoding="utf-8").read()
    lines = [repair_line(L) for L in raw.split("\n")]
    s = "\n".join(lines)
    try:
        d = json.loads(s)
    except Exception as e:
        print(fname, "PARSE FAIL:", e)
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
        return None
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
    return d


def report(fname, d):
    print(f"--- {fname}: {len(d)} entries")
    for f in d:
        fid = f.get("id")
        bio = len(f.get("biography") or "")
        ach = len(f.get("achievements") or [])
        sm = len(f.get("summary") or "")
        if bio < 380:
            print(f"  BIO SHORT {bio} {fid}")
        if ach < 6:
            print(f"  ACH SHORT {ach} {fid}")
        if not (30 <= sm <= 60):
            print(f"  SUMMARY LEN {sm} {fid}")
        for k in ("summary", "biography"):
            for m in LATIN.finditer(f.get(k) or ""):
                v = f[k]
                s = max(0, m.start() - 25)
                e = min(len(v), m.end() + 25)
                print(f"  LATIN[{k}] {m.group(0)!r} in {fid}: …{v[s:e]}…")
        for k in ("achievements", "quotes", "tags"):
            for it in (f.get(k) or []):
                for m in LATIN.finditer(str(it)):
                    print(f"  LATIN[{k}] {m.group(0)!r} in {fid}: {it}")
        for k in ("alias", "role", "lifeText"):
            for m in LATIN.finditer(str(f.get(k) or "")):
                print(f"  LATIN[{k}] {m.group(0)!r} in {fid}: {f.get(k)}")


if __name__ == "__main__":
    for fn in sys.argv[1:]:
        d = load(fn)
        if d is not None:
            report(fn, d)
