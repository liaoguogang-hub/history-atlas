# -*- coding: utf-8 -*-
"""Repair known typos in event shards."""
import io, os, re, sys

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"

FIXES = [
    ("阿育他\\code 的《阿基德史诗》", "阿育他的《阿基德史诗》"),
    ("阿育他code 的《阿基德史诗》", "阿育他的《阿基德史诗》"),
    ('"figures":fig-john-rome"', '"figures":[]'),
    ('"figures":fig-john-rome"', '"figures":[]'),
]


def repair(fname):
    path = os.path.join(TMP, fname)
    s = io.open(path, encoding="utf-8").read()
    orig = s
    for a, b in FIXES:
        s = s.replace(a, b)
    # generic: "figures":<non-array> -> []
    s = re.sub(r'"figures":(?!"\[)[^,\}]+', '"figures":[]', s)
    # generic: unescaped backslash before letters
    s = re.sub(r"\\(?=[A-Za-z])", "", s)
    if s != orig:
        io.open(path, "w", encoding="utf-8", newline="\n").write(s)
        print(fname, "repaired")
    else:
        print(fname, "no change")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        repair(f)
