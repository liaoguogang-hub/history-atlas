# -*- coding: utf-8 -*-
"""修复 figdata JSON：
1) CRLF -> LF（\r 是 JSON 字符串内的非法控制字符）
2) 畸形空 quotes 数组 ["",] -> []
3) 其它控制字符
"""
import glob
import io
import json
import re

PAT = re.compile(r'\[\s*""\s*,\s*"\]')
PAT2 = re.compile(r'\[\s*"\s*"\s*,\s*\]')
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

for f in sorted(glob.glob("figdata_*.json")):
    raw = io.open(f, "rb").read()
    # 1) 全部 CR 去掉
    raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    # 2) 畸形数组
    txt = raw.decode("utf-8")
    txt = PAT.sub("[]", txt)
    txt = PAT2.sub("[]", txt)
    txt = CTRL.sub("", txt)
    try:
        d = json.loads(txt)
    except Exception as e:
        print("STILL BAD", f, e)
        continue
    for p in d:
        p["q"] = [q for q in p.get("q", []) if isinstance(q, str) and q.strip()]
    with open(f, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(d, ensure_ascii=False, indent=1))
    print("%-20s %d ok" % (f, len(d)))
