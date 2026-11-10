# -*- coding: utf-8 -*-
"""定位 JSON 解析错误的确切位置。"""
import io

f = "figdata_03.json"
raw = io.open(f, encoding="utf-8", newline="").read()
lines = raw.split("\n")
for i in range(194, 200):
    print(i + 1, repr(lines[i]))
