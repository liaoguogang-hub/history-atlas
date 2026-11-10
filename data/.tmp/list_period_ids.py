# -*- coding: utf-8 -*-
"""列出 backup 中所有 period id，便于对齐。"""
import io
import re

s = io.open("periods_backup.py", encoding="utf-8").read()
ids = re.findall(r'"id": "(cn-[a-z0-9-]+)"', s)
print(len(ids))
for i in ids:
    print(i)
