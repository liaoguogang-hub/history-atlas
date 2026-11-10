# -*- coding: utf-8 -*-
"""逐字节定位解析失败位置。"""
import io
import json

f = "figdata_03.json"
raw = io.open(f, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
txt = raw.decode("utf-8")
try:
    json.loads(txt)
    print("OK")
except json.JSONDecodeError as e:
    print("err:", e)
    pos = e.pos
    print("context bytes:", repr(txt[pos - 80:pos + 40]))
    print("line:", e.lineno, "col:", e.colno)
