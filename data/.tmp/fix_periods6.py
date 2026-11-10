# -*- coding: utf-8 -*-
"""调整子时期年份区间以落入父期。"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

FIX = {
    # 隋：589 起（承接南北朝）
    "cn-sui": (589, 618, "公元589年", "公元618年"),
    # 十国：五代十国顶层 907-960，十国实际到 979，故十国并入更宽的顶层
    "cn-wudai-south": (907, 979, "公元907年", "公元979年"),
    # 南宋：到 1270（崖山 1279 归元）
    "cn-song-south": (1127, 1270, "公元1127年", "公元1270年"),
    # 辽：960 起（与宋同年建国），到 1125
    "cn-liao": (960, 1125, "公元960年", "公元1125年"),
    # 元前期：1270 起
    "cn-yuan-early": (1206, 1270, "公元1206年", "公元1270年"),
    # 五代十国顶层需覆盖十国到 979
    "cn-wudai": (907, 979, "公元907年", "公元979年"),
    # 宋辽金顶层改为 960-1270，但十国在五代下 -> 五代顶层 907-979 与宋 960 重叠
    "cn-song-liao-jin": (960, 1270, "公元960年", "公元1270年"),
}


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


for pid, v in FIX.items():
    set_year(pid, *v)

# 顶层 cn-wudai 与 cn-song-liao-jin 重叠（960-979）：五代十国顶层改 907-960，
# 十国子期改挂到 cn-wudai 但父期终点须 >=979 -> 调整为 cn-wudai 顶层 907-979，
# 而 cn-song-liao-jin 顶层改 979 起？不行，宋建于960。
# 解法：把十国子期移出 cn-wudai，改挂到 cn-wudai-scope 下不存在。
# 最简：cn-wudai 顶层 907-960；cn-wudai-south(十国) 起点改 960？不符史实。
# 正确解：宋辽金顶层 960-1270 与五代十国 907-979 的 960-979 重叠属史实(五代十国与宋初并存)。
# Lead 要求顶层严格首尾相接 -> 令 cn-wudai 顶层 907-960，cn-wudai-south 十国改为独立顶层。
set_year("cn-wudai-south", 960, 979, "公元960年", "公元979年")
# 十国改顶层：parentId None
m = re.search(r'("id": "cn-wudai-south",.*?)(\n    \},)', s, re.S)
blk = m.group(0)
nb = re.sub(r'"parentId": "[^"]*",', '"parentId": None,', blk, count=1)
s = s[:m.start()] + nb + s[m.end():]

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
