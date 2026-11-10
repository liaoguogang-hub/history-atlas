# -*- coding: utf-8 -*-
"""按 Lead 要求重构 periods 树：

1. 顶层 12-14 个：石器时代、夏商、西周、春秋战国、秦、西汉、东汉、三国两晋南北朝、
   隋、唐、五代十国、宋辽金、元、明、清、民国/近代、中华人民共和国
2. 每个时期 keyFigures 3-6、relatedEvents 3-8
3. 子时期年份精确落在父期内
"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- 顶层重排
# 旧 -> 新 parentId 映射
REPARENT = {
    # 夏商保持顶层；其下 cn-xia / cn-shang
    "cn-xia": "cn-xia-shang",
    "cn-shang": "cn-xia-shang",
    "cn-shang-early": "cn-shang",
    "cn-shang-late": "cn-shang",
    # 西周顶层化
    "cn-zhou-west": None,
    "cn-zhou-east": None,
    # 春秋、战国各自顶层化
    "cn-zhou-spring-autumn": None,
    "cn-zhou-warring-states": None,
    # 汉：西汉/东汉顶层化
    "cn-han-west": None,
    "cn-han-east": None,
    "cn-han-new": "cn-han-west",
    # 三国两晋南北朝
    "cn-three-kingdoms": "cn-wei-jin-nanbei",
    "cn-three-shu": "cn-three-kingdoms",
    "cn-three-wei": "cn-three-kingdoms",
    "cn-three-wu": "cn-three-kingdoms",
    "cn-liang-jin": "cn-wei-jin-nanbei",
    "cn-jin-west": "cn-liang-jin",
    "cn-jin-east": "cn-liang-jin",
    "cn-sixteen-kingdoms": "cn-wei-jin-nanbei",
    "cn-nanbei": "cn-wei-jin-nanbei",
    "cn-nanbei-north": "cn-nanbei",
    "cn-nanbei-south": "cn-nanbei",
    # 隋唐：隋与唐各自顶层化
    "cn-sui": None,
    "cn-tang": None,
    "cn-tang-early": "cn-tang",
    "cn-tang-mid": "cn-tang",
    "cn-tang-late": "cn-tang",
    # 五代十国
    "cn-wudai-north": "cn-wudai",
    "cn-wudai-south": "cn-wudai",
    # 宋辽金
    "cn-song-north": "cn-song-liao-jin",
    "cn-song-south": "cn-song-liao-jin",
    "cn-liao": "cn-song-liao-jin",
    "cn-jin": "cn-song-liao-jin",
    # 元
    "cn-yuan-early": "cn-yuan",
    "cn-yuan-late": "cn-yuan",
    # 明
    "cn-ming-early": "cn-ming",
    "cn-ming-mid": "cn-ming",
    "cn-ming-late": "cn-ming",
    # 清
    "cn-qing-early": "cn-qing",
    "cn-qing-mid": "cn-qing",
    "cn-qing-late": "cn-qing",
    # 近代
    "cn-modern-republic": "cn-modern",
    "cn-modern-anti-japan": "cn-modern",
    "cn-modern-liberation": "cn-modern",
    # 新中国
    "cn-prc-early": "cn-prc",
    "cn-prc-reform": "cn-prc",
    "cn-prc-new-era": "cn-prc",
}

# 需要提升为顶层（parentId=None）且重命名 id / 改名的
TOP_RENAME = {
    "cn-zhou-west": ("cn-zhou-west", "西周"),
    "cn-zhou-east": ("cn-zhou-east", "东周"),
    "cn-zhou-spring-autumn": ("cn-spring-autumn", "春秋"),
    "cn-zhou-warring-states": ("cn-warring-states", "战国"),
    "cn-han-west": ("cn-han-west", "西汉"),
    "cn-han-east": ("cn-han-east", "东汉"),
    "cn-sui": ("cn-sui", "隋"),
    "cn-tang": ("cn-tang", "唐"),
}

# 需要在 parentId=cn-wei-jin-nanbei 下的顶层（由 cn-wei-jin-nanbei 承���）
SPLIT_PARENT = {
    "cn-zhou-west": "cn-zhou-west",
    "cn-zhou-east": "cn-zhou-east",
}

# 旧 id -> 新 id
RENAME = {k: v[0] for k, v in TOP_RENAME.items()}
# 秦朝：新增
RENAME["cn-qin"] = "cn-qin"

blocks = re.findall(r'    \{\n        "id": "[^"]+",.*?\n    \},\n', s, re.S)
assert len(blocks) > 0, "no blocks"

# 分离头部与尾部
head_end = s.index(blocks[0])
head = s[:head_end]
tail_start = s.rindex("]\n")
tail = s[tail_start:]

out = []
for b in blocks:
    m = re.search(r'"id": "([^"]+)"', b)
    oid = m.group(1)
    nb = b
    # 重命名 id
    if oid in RENAME:
        nb = nb.replace('"id": "%s",' % oid, '"id": "%s",' % RENAME[oid], 1)
    # 重设 parentId
    if oid in REPARENT:
        newp = REPARENT[oid]
        if newp is None:
            nb = re.sub(r'"parentId": "[^"]*",', '"parentId": None,', nb, count=1)
        else:
            nb = re.sub(r'"parentId": "[^"]*",', '"parentId": "%s",' % newp, nb, count=1)
    out.append(nb)

# 修正重命名后引用了旧 id 的 parentId（REPARENT 里已用新名标注）
for old, new in RENAME.items():
    out = [b.replace('"parentId": "%s",' % old, '"parentId": "%s",' % new) for b in out]

# 调整顶层年份区间
YEARFIX = {
    "cn-zhou-west": (None, None, None),
    "cn-zhou-east": (None, None, None),
    "cn-spring-autumn": (None, None, None),
    "cn-warring-states": (None, None, None),
    "cn-han-west": (None, None, None),
    "cn-han-east": (None, None, None),
    "cn-sui": (None, None, None),
    "cn-tang": (None, None, None),
}
for b in out:
    m = re.search(r'"id": "([^"]+)"', b)
    pid = m.group(1)
    if pid in YEARFIX:
        b = re.sub(r'"startYear": -?\d+,', '"startYear": -1046,', b, count=1)
        b = re.sub(r'"endYear": -?\d+,', '"endYear": -771,', b, count=1)

# 秦朝块：插入到 cn-xia-shang 之前
QIN = '''    {
        "id": "cn-qin",
        "name": "秦",
        "alias": "秦朝",
        "parentId": None,
        "startYear": -221,
        "endYear": -207,
        "startDateText": "公元前221年",
        "endDateText": "公元前207年",
        "colorKey": "blue",
        "summary": "中国第一个统一的中央集权王朝，享国仅十五年却奠定了此后两千年的政治制度格局。秦王嬴政十年之间先后灭韩、赵、魏、楚、燕、齐，结束春秋战国五百余年的分裂，于公元前221年称皇帝并定都咸阳。秦以三公九卿与郡县制取代分封，废六国文字而统一为小篆，统一度量衡与车轨，颁行《秦律》，铸半两钱与圆形方孔钱通行全国。修筑长城连接燕、赵、秦旧塞，筑驰道直道通全国，北击匈奴，南取百越，设桂林、象郡、南海三郡。焚书坑儒、严刑峻法激起反抗，前209年陈胜吴广起义爆发，前207年秦亡，其速亡成为后世王朝吸取教训的核心案例。",
        "territory": "东至东海与朝鲜半岛北部，西至临洮、羌中，南抵南海象郡，北至长城与河套",
        "capital": "咸阳",
        "population": "约二千万（估算）",
        "culture": "秦篆与隶书；皇帝制度与三公九卿、郡县制；统一度量衡与货币；《秦律》与严刑；驰道与长城",
        "keyFigures": ["fig-qin-shi-huang", "fig-li-si", "fig-zhao-gao", "fig-huang-jie", "fig-zhang-liang"],
        "relatedEvents": ["ev-qin-unify", "ev-qin-emperor-system", "ev-qin-county-system", "ev-qin-standardize", "ev-qin-burn-books", "ev-qin-great-wall", "ev-qin-li-si", "ev-qin-liuxiang", "ev-qin-chensheng", "ev-qin-fall"],
        "tags": ["秦", "统一", "中央集权", "郡县制", "始皇"],
    },
'''
idx = next(i for i, b in enumerate(out) if '"id": "cn-xia-shang"' in b)
out.insert(idx, QIN)

s = head + "".join(out) + tail
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("restructured, blocks:", len(out))
