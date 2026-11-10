# -*- coding: utf-8 -*-
"""校验 figures 批次。"""
import importlib.util
import sys
import glob
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_builder import build

errs = []
all_figs = []
seen = set()

files = sorted(glob.glob("figs_b*.py"))
for f in files:
    spec = importlib.util.spec_from_file_location(os.path.splitext(f)[0], f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    figs = build(m.R)
    for fg in figs:
        if fg["id"] in seen:
            errs.append("DUP %s in %s" % (fg["id"], f))
        seen.add(fg["id"])
        sl = len(fg["summary"])
        if not (40 <= sl <= 120):
            errs.append("SUMMARY %s len=%d" % (fg["id"], sl))
        bl = len(fg["biography"])
        if not (200 <= bl <= 1000):
            errs.append("BIO %s len=%d" % (fg["id"], bl))
        if not (3 <= len(fg["achievements"]) <= 6):
            errs.append("ACH %s n=%d" % (fg["id"], len(fg["achievements"])))
        if len(fg["quotes"]) > 3:
            errs.append("QUOTES %s n=%d" % (fg["id"], len(fg["quotes"])))
        if fg["birthYear"] is not None and fg["deathYear"] is not None:
            if fg["birthYear"] > fg["deathYear"]:
                errs.append("YEAR %s %d>%d" % (fg["id"], fg["birthYear"], fg["deathYear"]))
        if not fg["role"] or not fg["gender"] or not fg["periodId"]:
            errs.append("FIELD %s" % fg["id"])
        if fg["gender"] not in ("male", "female", "unknown"):
            errs.append("GENDER %s %s" % (fg["id"], fg["gender"]))
    all_figs.extend(figs)
    print("%-18s %3d figures" % (f, len(figs)))

print("TOTAL:", len(all_figs))
if errs:
    print("\n=== ERRORS (%d) ===" % len(errs))
    for e in errs:
        print(" ", e)
    sys.exit(1)
print("OK")
