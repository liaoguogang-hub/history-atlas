# -*- coding: utf-8 -*-
"""第三轮：重建 periods 树为 Lead 要求的最终结构。

做法：解析 backup 里的所有块 -> 建立 id->block 字典 -> 按目标结构重新组装。
保留每个块原有的 summary/territory/capital/... 等内容，只改 id/name/parentId/年份。
"""
import io
import re
import collections

SRC = "periods_backup.py"
DST = "periods_data.py"

s = io.open(SRC, encoding="utf-8").read()
blocks = re.findall(r'    \{\n        "id": "([^"]+)",.*?\n    \},\n', s, re.S)
# 重新切出原文块
raw_blocks = re.findall(r'    \{\n        "id": "[^"]+",.*?\n    \},\n', s, re.S)
assert len(raw_blocks) == len(blocks), (len(raw_blocks), len(blocks))

B = {}
for bid, b in zip(blocks, raw_blocks):
    B[bid] = b


def mk(bid, name, parent, sy, ey, sdt, edt, newid=None, color=None, alias=None):
    """基于 backup 中 bid 的块，改写关键字段。"""
    src = B.get(bid)
    if src is None:
        raise KeyError(bid)
    nb = src
    nid = newid or bid
    nb = nb.replace('"id": "%s",' % bid, '"id": "%s",' % nid, 1)
    if name:
        nb = re.sub(r'"name": "[^"]*",', '"name": "%s",' % name, nb, count=1)
    if alias:
        nb = re.sub(r'"alias": "[^"]*",', '"alias": "%s",' % alias, nb, count=1)
    nb = re.sub(r'"parentId": ("[^"]*"|None),', '"parentId": %s,' % ('None' if parent is None else '"%s"' % parent), nb, count=1)
    nb = re.sub(r'"startYear": -?\d+,', '"startYear": %d,' % sy, nb, count=1)
    nb = re.sub(r'"endYear": -?\d+,', '"endYear": %d,' % ey, nb, count=1)
    nb = re.sub(r'"startDateText": "[^"]*",', '"startDateText": "%s",' % sdt, nb, count=1)
    nb = re.sub(r'"endDateText": "[^"]*",', '"endDateText": "%s",' % edt, nb, count=1)
    if color:
        nb = re.sub(r'"colorKey": "[^"]*",', '"colorKey": "%s",' % color, nb, count=1)
    return nb


BC = "公元前%d年"
def bc(y):
    return BC % y

out = []

# ============ 顶层 14 个 ============
# 1 石器时代
out.append(mk("cn-prehistory", "史前时代", None, -2070000, -2001,
               "公元前207万年", "公元前2001年", color="stone", alias="石器时代"))
# 2 夏商
out.append(mk("cn-xia-shang", "夏商", None, -2070, -1046, bc(-2070), bc(-1046),
               color="cyan", alias="夏朝与商朝"))
# 3 西周
out.append(mk("cn-zhou-west", "西周", None, -1046, -771, bc(-1046), bc(-771),
               color="zhou", alias="镐京时期"))
# 4 春秋战国
out.append(mk("cn-zhou-east", "春秋战国", None, -770, -256, bc(-770), bc(-256),
               color="zhou", alias="东周"))
# 5 秦
out.append(mk("cn-qin", "秦", None, -221, -207, bc(-221), bc(-207),
               color="blue", alias="秦朝"))
# 6 汉
out.append(mk("cn-han", "汉", None, -202, 220, bc(-202), "公元220年",
               color="han", alias="汉朝"))
# 7 三国两晋南北朝
out.append(mk("cn-wei-jin-nanbei", "三国两晋南北朝", None, 220, 589, "公元220年", "公元589年",
               color="green", alias="分裂与融合时期"))
# 8 隋唐
out.append(mk("cn-sui-tang", "隋唐", None, 581, 907, "公元581年", "公元907年",
               color="sui-tang", alias="隋朝与唐朝"))
# 9 五代十国
out.append(mk("cn-wudai", "五代十国", None, 907, 979, "公元907年", "公元979年",
               color="yellow", alias="五代十国"))
# 10 宋辽金
out.append(mk("cn-song-liao-jin", "宋辽金", None, 960, 1279, "公元960年", "公元1279年",
               color="yellow", alias="宋辽金时期"))
# 11 元
out.append(mk("cn-yuan", "元", None, 1206, 1368, "公元1206年", "公元1368年",
               color="yuan", alias="元朝"))
# 12 明
out.append(mk("cn-ming", "明", None, 1368, 1644, "公元1368年", "公元1644年",
               color="pink", alias="明朝"))
# 13 清
out.append(mk("cn-qing", "清", None, 1644, 1912, "公元1644年", "公元1912年",
               color="qing", alias="清朝"))
# 14 民国/近代
out.append(mk("cn-modern", "近代", None, 1912, 1949, "公元1912年", "公元1949年",
               color="gray", alias="民国与近代"))
# 15 中华人民共和国
out.append(mk("cn-prc", "中华人民共和国", None, 1949, 2026, "公元1949年", "至今",
               color="modern", alias="新中国"))

# ============ 二级 / 三级 ============
# 史前
out.append(mk("cn-pre-paleolithic", "旧石器时代", "cn-prehistory", -2070000, -12000,
               "公元前207万年", bc(-12000), alias="猿人时期"))
out.append(mk("cn-pre-neolithic", "新石器时代", "cn-prehistory", -12000, -2070,
               bc(-12000), bc(-2070), alias="农业文明曙光"))
# 夏商
out.append(mk("cn-xia", "夏", "cn-xia-shang", -2070, -1600, bc(-2070), bc(-1600),
               alias="夏朝、夏后氏"))
out.append(mk("cn-shang", "商", "cn-xia-shang", -1600, -1046, bc(-1600), bc(-1046),
               alias="商朝、殷商"))
out.append(mk("cn-shang-early", "早商", "cn-shang", -1600, -1300, bc(-1600), bc(-1300),
               alias="商前期"))
out.append(mk("cn-shang-late", "晚商", "cn-shang", -1300, -1046, bc(-1300), bc(-1046),
               alias="殷商"))
# 春秋战国
out.append(mk("cn-spring-autumn", "春秋", "cn-zhou-east", -770, -476, bc(-770), bc(-476),
               alias="春秋时期、诸侯争霸"))
out.append(mk("cn-warring-states", "战国", "cn-zhou-east", -475, -256, bc(-475), bc(-256),
               alias="战国七雄"))
# 汉：顶层用 cn-han（原西汉内容改写），西汉用原 cn-han-west 块
out.append(mk("cn-han-west", "西汉", "cn-han", -202, 9, bc(-202), "公元9年",
               alias="前汉"))
out.append(mk("cn-han-new", "新朝", "cn-han", 9, 23, "公元9年", "公元23年",
               alias="王莽新朝"))
out.append(mk("cn-han-east", "东汉", "cn-han", 25, 220, "公元25年", "公元220年",
               alias="后汉"))
# 三国两晋南北朝
out.append(mk("cn-three-kingdoms", "三国", "cn-wei-jin-nanbei", 220, 280, "公元220年", "公元280年",
               alias="魏蜀吴"))
out.append(mk("cn-three-shu", "蜀汉", "cn-three-kingdoms", 221, 263, "公元221年", "公元263年",
               alias="蜀"))
out.append(mk("cn-three-wei", "曹魏", "cn-three-kingdoms", 220, 265, "公元220年", "公元265年",
               alias="魏"))
out.append(mk("cn-three-wu", "孙吴", "cn-three-kingdoms", 222, 280, "公元222年", "公元280年",
               alias="吴"))
out.append(mk("cn-liang-jin", "两晋", "cn-wei-jin-nanbei", 265, 420, "公元265年", "公元420年",
               alias="晋朝"))
out.append(mk("cn-jin-west", "西晋", "cn-liang-jin", 265, 316, "公元265年", "公元316年",
               alias="晋武帝时期"))
out.append(mk("cn-jin-east", "东晋", "cn-liang-jin", 317, 420, "公元317年", "公元420年",
               alias="建康时期"))
out.append(mk("cn-sixteen-kingdoms", "十六国", "cn-wei-jin-nanbei", 304, 439, "公元304年", "公元439年",
               alias="五胡十六国"))
out.append(mk("cn-nanbei", "南北朝", "cn-wei-jin-nanbei", 420, 589, "公元420年", "公元589年",
               alias="南北对峙"))
out.append(mk("cn-nanbei-north", "北朝", "cn-nanbei", 386, 581, "公元386年", "公元581年",
               alias="北魏及东晋北朝"))
out.append(mk("cn-nanbei-south", "南朝", "cn-nanbei", 420, 589, "公元420年", "公元589年",
               alias="宋齐梁陈"))
# 隋唐
out.append(mk("cn-sui", "隋", "cn-sui-tang", 581, 618, "公元581年", "公元618年",
               alias="隋朝"))
out.append(mk("cn-tang", "唐", "cn-sui-tang", 618, 907, "公元618年", "公元907年",
               alias="唐朝"))
out.append(mk("cn-tang-early", "唐前期", "cn-tang", 618, 755, "公元618年", "公元755年",
               alias="贞观开元"))
out.append(mk("cn-tang-mid", "唐中期", "cn-tang", 755, 827, "公元755年", "公元827年",
               alias="安史之乱至中兴"))
out.append(mk("cn-tang-late", "唐后期", "cn-tang", 827, 907, "公元827年", "公元907年",
               alias="晚唐"))
# 五代十国
out.append(mk("cn-wudai-north", "五代", "cn-wudai", 907, 960, "公元907年", "公元960年",
               alias="五代中原"))
out.append(mk("cn-wudai-south", "十国", "cn-wudai", 907, 979, "公元907年", "公元979年",
               alias="南方割据"))
# 宋辽金
out.append(mk("cn-song-north", "北宋", "cn-song-liao-jin", 960, 1127, "公元960年", "公元1127年",
               alias="北宋"))
out.append(mk("cn-song-south", "南宋", "cn-song-liao-jin", 1127, 1279, "公元1127年", "公元1279年",
               alias="临安时期"))
out.append(mk("cn-liao", "辽", "cn-song-liao-jin", 916, 1125, "公元916年", "公元1125年",
               alias="契丹国"))
out.append(mk("cn-jin", "金", "cn-song-liao-jin", 1115, 1234, "公元1115年", "公元1234年",
               alias="女真金"))
# 元
out.append(mk("cn-yuan-early", "元前期", "cn-yuan", 1206, 1271, "公元1206年", "公元1271年",
               alias="蒙古帝国与元初"))
out.append(mk("cn-yuan-late", "元后期", "cn-yuan", 1271, 1368, "公元1271年", "公元1368年",
               alias="元朝中后期"))
# 明
out.append(mk("cn-ming-early", "明前期", "cn-ming", 1368, 1521, "公元1368年", "公元1521年",
               alias="洪武至正德"))
out.append(mk("cn-ming-mid", "明中期", "cn-ming", 1521, 1620, "公元1521年", "公元1620年",
               alias="嘉靖隆庆万历"))
out.append(mk("cn-ming-late", "明后期", "cn-ming", 1620, 1644, "公元1620年", "公元1644年",
               alias="晚明"))
# 清
out.append(mk("cn-qing-early", "清前期", "cn-qing", 1644, 1735, "公元1644年", "公元1735年",
               alias="顺治至雍正"))
out.append(mk("cn-qing-mid", "清中期", "cn-qing", 1735, 1820, "公元1735年", "公元1820年",
               alias="乾隆至嘉庆"))
out.append(mk("cn-qing-late", "清后期", "cn-qing", 1820, 1912, "公元1820年", "公元1912年",
               alias="晚清"))
# 近代
out.append(mk("cn-modern-republic", "民国初年", "cn-modern", 1912, 1927, "公元1912年", "公元1927年",
               alias="北洋政府时期"))
out.append(mk("cn-modern-anti-japan", "抗日战争", "cn-modern", 1931, 1945, "公元1931年", "公元1945年",
               alias="抗日战争时期"))
out.append(mk("cn-modern-liberation", "解放战争", "cn-modern", 1945, 1949, "公元1945年", "公元1949年",
               alias="人民解放战争"))
# 新中国
out.append(mk("cn-prc-early", "社会主义革命与建设时期", "cn-prc", 1949, 1978, "公元1949年", "公元1978年",
               alias="1949—1978"))
out.append(mk("cn-prc-reform", "改革开放新时期", "cn-prc", 1978, 2012, "公元1978年", "公元2012年",
               alias="1978—2012"))
out.append(mk("cn-prc-new-era", "新时代", "cn-prc", 2012, 2026, "公元2012年", "至今",
               alias="中国特色社会主义新时代"))

head = s[:s.index(raw_blocks[0])]
tail = s[s.rindex("]\n"):]
new = head + "".join(out) + tail
io.open(DST, "w", encoding="utf-8", newline="\n").write(new)
print("wrote", len(out), "blocks")
