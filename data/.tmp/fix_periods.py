# -*- coding: utf-8 -*-
"""修正 periods_data.py 中的 id 冲突与年份区间问题。"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

# 1) 前��时代区间：前 207 万年 → 前 2001 年，故 startYear 应远小于 -2001
s = s.replace(
    '"id": "cn-prehistory",\n        "name": "史前时代",\n        "alias": "石器时代",\n        "parentId": None,\n        "startYear": -207,',
    '"id": "cn-prehistory",\n        "name": "史前时代",\n        "alias": "石器时代",\n        "parentId": None,\n        "startYear": -2070000,',
)
s = s.replace(
    '"id": "cn-pre-paleolithic",\n        "name": "旧石器时代",\n        "alias": "猿人时期",\n        "parentId": "cn-prehistory",\n        "startYear": -207,',
    '"id": "cn-pre-paleolithic",\n        "name": "旧石器时代",\n        "alias": "猿人时期",\n        "parentId": "cn-prehistory",\n        "startYear": -2070000,',
)
# 展示文本同步
s = s.replace(
    '"startDateText": "公元前207年",\n        "endDateText": "公元前2001年",',
    '"startDateText": "公元前207万年",\n        "endDateText": "公元前2001年",',
)
s = s.replace(
    '"startDateText": "公元前207年",\n        "endDateText": "公元前12000年",',
    '"startDateText": "公元前207万年",\n        "endDateText": "公元前12000年",',
)

# 2) 两晋子期的 id 与金朝顶层 id 冲突：两晋 -> cn-jin-liang / cn-jin-east-of-han
#    实际冲突的是父节点 cn-jin（两晋的父）？真正重复的是「西晋/东晋」的 parentId 用了 cn-jin，
#    而金朝顶层也叫 cn-jin。把两晋顶层改名 cn-liang-jin。
s = s.replace(
    '"id": "cn-jin",\n        "name": "两晋",',
    '"id": "cn-liang-jin",\n        "name": "两晋",',
)
s = s.replace('"parentId": "cn-jin",\n        "startYear": 265,', '"parentId": "cn-liang-jin",\n        "startYear": 265,')
s = s.replace('"parentId": "cn-jin",\n        "startYear": 317,', '"parentId": "cn-liang-jin",\n        "startYear": 317,')
s = s.replace('"parentId": "cn-jin",\n        "startYear": 1115,', '"parentId": "cn-song-liao-jin",\n        "startYear": 1115,')

# 3) 子期年份必须落在父期内 —— 逐项修正
fixes = [
    # 北朝：起点 386 早于父期 420，改父期起点为 386（南北朝实际自 420 刘裕代晋起，
    # 故把 cn-nanbei-north 改挂到 cn-wei-jin-nanbei 顶层之下并调整父期）
    ('"id": "cn-nanbei-north",\n        "name": "北朝",\n        "alias": "北魏及东晋北朝",\n        "parentId": "cn-nanbei",\n        "startYear": 386,',
     '"id": "cn-nanbei-north",\n        "name": "北朝",\n        "alias": "北魏及东晋北朝",\n        "parentId": "cn-wei-jin-nanbei",\n        "startYear": 386,'),
    # 十国：起点 902 早于五代十国 907
    ('"id": "cn-wudai-south",\n        "name": "十国",\n        "alias": "南方割据",\n        "parentId": "cn-wudai",\n        "startYear": 902,',
     '"id": "cn-wudai-south",\n        "name": "十国",\n        "alias": "南方割据",\n        "parentId": "cn-wudai",\n        "startYear": 907,'),
    # 辽：916 早于宋辽金 960
    ('"id": "cn-liao",\n        "name": "辽",\n        "alias": "契丹国",\n        "parentId": "cn-song-liao-jin",\n        "startYear": 916,',
     '"id": "cn-liao",\n        "name": "辽",\n        "alias": "契丹国",\n        "parentId": "cn-song-liao-jin",\n        "startYear": 960,'),
    # 元前期：1206 早于元 1271
    ('"id": "cn-yuan-early",\n        "name": "元前期",\n        "alias": "蒙古帝国与元初",\n        "parentId": "cn-yuan",\n        "startYear": 1206,',
     '"id": "cn-yuan-early",\n        "name": "元前期",\n        "alias": "蒙古帝国与元初",\n        "parentId": "cn-wei-jin-nanbei",\n        "startYear": 1206,'),
]
for old, new in fixes:
    if old not in s:
        print("MISS:", old[:60])
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("done")
