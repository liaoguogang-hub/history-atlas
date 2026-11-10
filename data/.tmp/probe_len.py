# -*- coding: utf-8 -*-
"""诊断：检查 summary 实际字符数。"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_builder import build

spec = importlib.util.spec_from_file_location("b1", "figs_b01.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
figs = build(m.R)
for fg in figs[:6]:
    print(fg["id"])
    print("  summary:", repr(fg["summary"]))
    print("  len:", len(fg["summary"]))
