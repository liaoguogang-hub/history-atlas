# -*- coding: utf-8 -*-
"""打印出错行的原始字节。"""
import io

f = "figdata_03.json"
raw = io.open(f, "rb").read()
lines = raw.split(b"\n")
print("196:", lines[196])
print("197:", lines[196].hex())
