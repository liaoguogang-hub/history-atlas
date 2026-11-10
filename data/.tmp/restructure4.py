# -*- coding: utf-8 -*-
"""第四轮：修正父子年份区间，并把顶层压到 14 个。

处理：
1. cn-song-liao-jin 起点 960 -> 916（辽 916 建国）
2. cn-nanbei 起点 420 -> 386（北朝 386 建北魏）
3. 顶层 15 -> 14：把 cn-prehistory 并入 cn-xia-shang 之下的子期？
   不。更合理：把「夏商」并入「石器时代」？不合适。
   改法：把 cn-qin 降为 cn-zhou-east 的子期？秦不属于东周。
   最合理：合并 cn-spring-autumn/cn-warring-states 已完成；
   把「民国/近代」与「清」分开保留 —— Lead 明确要「民国/近代」顶层。
   那就合并「石器时代」与「夏商」为一个顶层「史前至夏商」？Lead 分列二者。
   实际 Lead 列表 17 项，合并「西汉/东汉→汉」「隋/唐→隋唐」得 15。
   再合并一项：把「石器时代」并入顶层但作为 cn-prehistory 保留（已在）。
   => 接受 15 个，并在报告中说明（Lead 允许「可微调」）。
   或者：把「三国两晋南北朝」与「隋唐」合并？不合理。
   最终：15 个顶层。折中到 14：把 cn-qin 降级为 cn-zhou-east 的子期不合逻辑，
   改为把 cn-spring-autumn 与 cn-warring-states 保持，
   并把「清后期(晚清)」保持……
   决定：保持 15 个顶层（Lead 12-14 附近，且列表本身 17 项）。
"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()


def set_year(bid, field, val, text=None):
    global s
    m = re.search(r'("id": "%s",.*?)(\n    \},)' % re.escape(bid), s, re.S)
    if not m:
        raise KeyError(bid)
    blk = m.group(0)
    nb = re.sub(r'"%sYear": -?\d+,' % field, '"%sYear": %d,' % (field, val), blk, count=1)
    if text is not None:
        tfield = field.replace("Year", "DateText")
        nb = re.sub(r'"%s": "[^"]*",' % tfield, '"%s": "%s",' % (tfield, text), nb, count=1)
    s = s[:m.start()] + nb + s[m.end():]


# 1) 宋辽金 起点 -> 916
set_year("cn-song-liao-jin", "start", 916, "公元916年")
# 2) 南北朝 起点 -> 386
set_year("cn-nanbei", "start", 386, "公元386年")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
