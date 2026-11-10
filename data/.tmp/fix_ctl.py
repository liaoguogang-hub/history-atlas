# -*- coding: utf-8 -*-
"""找出并修复 JSON 字符串内的换行/控制字符。"""
import io
import re

f = "figdata_03.json"
raw = io.open(f, encoding="utf-8", newline="").read()
lines = raw.split("\n")
print("line 146:")
print(repr(lines[145]))
print("line 147:")
print(repr(lines[146]))
