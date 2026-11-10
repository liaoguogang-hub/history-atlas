# -*- coding: utf-8 -*-
"""Repair world_figures_p1.json: fix broken achievements, remove duplicate Ibn Khaldun."""
import io, os, re

TMP = r"C:\Users\guoga\Documents\DSH\data\.tmp"
P = os.path.join(TMP, "world_figures_p1.json")
s = io.open(P, encoding="utf-8").read()

# 1) Fix fig-darius achievements: find the broken segment and replace it
start = s.find('"achievements":"平定帝国全境叛乱')
if start != -1:
    # the broken entry runs until the next '],"quotes"'
    end = s.find('],"quotes"', start)
    new_ach = ('"achievements":["平定帝国全境叛乱，重建居鲁士去世后濒临瓦解的统治秩序",'
               '"确立行省制、贡赋统一与标准化铸币体系",'
               '"修筑御道与驿传，建立古代世界规模最大的王室通信网络",'
               '"颁布《贝希特敦铭文》等王室宣教文本",'
               '"波斯波利斯宫殿与浮雕成为古代波斯艺术的巅峰",'
               '"其改革为后世亚历山大、塞琉古与萨法维波斯所继承",'
               '"促成耶路撒冷圣殿的重建与宗教宽容政策",'
               '"亲率帝国舰队与运河工程完成对阿拉伯的远征",'
               '"将波斯传统与阿卡德、埃兰的行政技术深度融合",'
               '"在位时波斯帝国达到疆域与组织度的极盛"')
    s = s[:start] + new_ach + s[end:]
    print("fixed fig-darius achievements")

# 2) Remove the duplicate fig-ibn-khaldun-2 entry entirely
i = s.find('{"id":"fig-ibn-khaldun-2"')
if i != -1:
    # it is the last entry; find the closing of the array
    j = s.find('\n]', i)
    s = s[:i].rstrip().rstrip(',') + s[j:]
    print("removed fig-ibn-khaldun-2")

# 3) remove leftover 'royal 邮递官' latin
s = s.replace("royal 邮递官", "御用邮递官")
# 4) remove remaining stray latin in p1
s = s.replace("Alexandros 时期", "亚历山大时期")
s = s.replace("Musica 的形式", "音乐的形式")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written")
