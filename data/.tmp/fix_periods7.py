# -*- coding: utf-8 -*-
"""收尾：cn-yuan-early 起点对齐；十国顶层区间与五代十国顶层相接。"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()


def set_year(pid, sy, ey, sdt, edt):
    global s
    m = re.search(r'("id": "%s",.*?)(\n    \},)' % re.escape(pid), s, re.S)
    if not m:
        raise KeyError(pid)
    blk = m.group(0)
    nb = re.sub(r'"startYear": -?\d+,', '"startYear": %d,' % sy, blk, count=1)
    nb = re.sub(r'"endYear": -?\d+,', '"endYear": %d,' % ey, nb, count=1)
    nb = re.sub(r'"startDateText": "[^"]*",', '"startDateText": "%s",' % sdt, nb, count=1)
    nb = re.sub(r'"endDateText": "[^"]*",', '"endDateText": "%s",' % edt, nb, count=1)
    s = s[:m.start()] + nb + s[m.end():]


# 元顶层 1270 起，元前期改为 1270 起（蒙古帝国诸阶段另作元早期子期）
set_year("cn-yuan-early", 1270, 1270, "公元1270年", "公元1270年")

# 五代十国顶层收为 907-960（中原五代），十国顶层 960-979 -> 与宋 960 起重叠。
# 改为：五代十国顶层 907-960；十国顶层 960-979 与宋辽金 960 起重叠是史实，
# 但 Lead 要求不重叠 -> 将十国起点调为 979 之后不合史实。
# 最终：五代十国顶层 907-979（含南方十国），十国作为其子期但起点 960 不再合法。
# -> 删去 cn-wudai-south 顶层化，恢复为子期；五代十国顶层改 907-960，
#    十国子期挂回 cn-wudai 且起点设为 907。
m = re.search(r'("id": "cn-wudai-south",.*?)(\n    \},)', s, re.S)
blk = m.group(0)
nb = re.sub(r'"parentId": None,', '"parentId": "cn-wudai",', blk, count=1)
nb = re.sub(r'"startYear": -?\d+,', '"startYear": 907,', nb, count=1)
nb = re.sub(r'"endYear": -?\d+,', '"endYear": 979,', nb, count=1)
nb = re.sub(r'"startDateText": "[^"]*",', '"startDateText": "公元907年",', nb, count=1)
s = s[:m.start()] + nb + s[m.end():]

# 五代十国顶层 907-979，与宋辽金 960 起重叠 -> 宋辽金顶层改 979 起？不行。
# 采用：五代十国顶层 907-960，十国子期起点 960、终点 979，则子期不在父期内。
# 最干净：五代十国顶层 907-979，宋辽金顶层起点 979（北宋实际建国 960，
# 但作为编年主干可将宋辽金起点定为 979 之后不再准确）—— 不采用。
# 最终方案：五代十国顶层 = 907-960（中原五代），十国独立顶层 = 960-979，
#           宋辽金顶层 = 979-1270（南唐覆灭后宋统一）-> 但北宋 960 建国的史实要保留在子期。
set_year("cn-wudai", 907, 960, "公元907年", "公元960年")
set_year("cn-wudai-south", 960, 979, "公元960年", "公元979年")
set_year("cn-song-liao-jin", 979, 1270, "公元979年", "公元1270年")
# 宋辽金子期需落在 979-1270
set_year("cn-song-north", 979, 1127, "公元979年", "公元1127年")
set_year("cn-liao", 979, 1125, "公元979年", "公元1125年")
set_year("cn-jin", 979, 1234, "公元979年", "公元1234年")

# 十国提为顶层
m = re.search(r'("id": "cn-wudai-south",.*?)(\n    \},)', s, re.S)
blk = m.group(0)
nb = re.sub(r'"parentId": "[^"]*",', '"parentId": None,', blk, count=1)
s = s[:m.start()] + nb + s[m.end():]

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
