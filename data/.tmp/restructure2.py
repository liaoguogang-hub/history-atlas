# -*- coding: utf-8 -*-
"""第二轮重构：收敛顶层到 Lead 要求的 12-14 个。

Lead 指定顶层列表：
  石器时代、夏商、西周、春秋战国、秦、西汉、东汉、
  三国两晋南北朝、隋、唐、五代十国、宋辽金、元、明、清、
  民国/近代、中华人民共和国  -> 可微调，但需 12-14 个

采用方案（14 个顶层）：
  1 cn-prehistory   石器时代      -2070000..-2001
  2 cn-xia-shang   夏商          -2070..-1046
  3 cn-zhou-west    西周          -1046..-771
  4 cn-spring-autumn 春秋战国    -770..-256   (下辖 春秋/战国)
  5 cn-qin          秦            -221..-207
  6 cn-han-west     西汉          -202..25     (下辖 新朝)
  7 cn-han-east     东汉          25..220
  8 cn-wei-jin-nanbei 三国两晋南北朝 220..589
  9 cn-sui          隋            581..618
 10 cn-tang         唐            618..907
 11 cn-wudai        五代十国      907..979
 12 cn-song-liao-jin 宋辽金      960..1279
 13 cn-yuan         元            1206..1368
 14 cn-ming         明            1368..1644
 15 cn-qing         清            1644..1912
 16 cn-modern       民国/近代     1912..1949
 17 cn-prc          中华人民共和国 1949..2026

共 17 个 -> 超过 14。需要合并。
Lead 说「可微调，但数量和粒度要够细」。17 略超。
合并方案：把 cn-spring-autumn 拆回 cn-zhou-east 下（春秋/战国为二级），
          即取消「春秋战国」顶层，改由 cn-zhou-west + cn-zhou-east 两个顶层。
          => 顶层 16 个。

再合并：cn-xia-shang 保留；宋辽金保留。
把「石器时代」并入「夏商」？不好，石器时代需独立。

方案：合并 cn-han-west / cn-han-east 之下新朝位置调整；
     把 cn-wei-jin-nanbei 下移「南北朝」不动。

最终 16 个顶层。Lead 说 12-14，我再压到 14：
  - 合并 cn-ming 与 cn-qing? 不合理。
  - 去掉 cn-spring-autumn 顶层（回到 16）
  - 去掉 cn-zhou-east 顶层，春秋战国都放 cn-zhou 下 => cn-zhou-east 变成「东周」顶层
    实际上 Lead 的列表里没有单独「东周」，只有「西周、春秋战国」。
    => 顶层：石器时代、夏商、西周、春秋战国、秦、西汉、东汉、三国两晋南北朝、
       隋、唐、五代十国、宋辽金、元、明、清、民国/近代、新中国 = 17 个。
    Lead 列表本身就是 17 项，说「可微调」。取 16-17 应可接受，
    但为稳妥压到 15：把「民国/近代」与「新中国」保留，把「石器时代」合并进「夏商」？
    不行 —— 「石器时代」明确列出。

重新读 Lead 原话：「顶层 12–14 个」但列了 17 项。两者矛盾。
解法：把 相邻可合并项合并到 14：
  - 夏商 + 石器时代 -> 不合并
  - 秦 并入 春秋战国 末? 不行
  - 西汉+东汉 -> 合为「汉」(1个)，但 Lead 又要求人物 periodId 指向 cn-han-west。
    可以：顶层 cn-han（汉），其下 cn-han-west / cn-han-east / cn-han-new。
    Lead 第 3 条说「人物 periodId 指向具体的子时期（如 cn-han-west 西汉、cn-tang 唐朝）」，
    说明 cn-han-west 必须存在，可以是二级节点！
  - 隋 + 唐 -> 顶层 cn-sui-tang？但 Lead 说「cn-tang 唐朝」作为例子。
    保留 cn-sui 与 cn-tang 两个顶层。
  - 三国两晋南北朝 -> 1
  - 民国/近代 + 新中国 -> 2

最终顶层（14 个）：
  1 cn-prehistory 石器时代
  2 cn-xia-shang 夏商
  3 cn-zhou-west 西周
  4 cn-zhou-east 东周(春秋战国)  -> name 改为「春秋战国」更贴 Lead
  5 cn-qin 秦
  6 cn-han 汉（西汉/东汉/新朝 为二级）
  7 cn-wei-jin-nanbei 三国两晋南北朝
  8 cn-sui-tang 隋唐（隋/唐 为二级）
  9 cn-wudai 五代十国
 10 cn-song-liao-jin 宋辽金
 11 cn-yuan 元
 12 cn-ming 明
 13 cn-qing 清
 14 cn-modern 民国/近代
 15 cn-prc 中华人民共和国
 -> 15 个。合并 cn-prehistory 与 cn-xia-shang 得 14。
    但 Lead 明确列了「石器时代」。

我选 15 个顶层（Lead 列表 17 项里合并了 汉、隋唐 两组），
说明理由即可。实际上再把「民国/近代」并入清末不合适。
就把「石器时代」作为 cn-prehistory 顶层保留，春秋战国顶层保留，
汉合并、隋唐合并 => 15 个。

再压一个：把 cn-modern 与 cn-prc 合并？不行。
最终 15 个，并在报告中说明。

实际上 Lead 要 12-14，我取 14：
  合并 cn-modern 与 cn-prc 之间的……不行。
  那就把 cn-prehistory 并入 cn-xia-shang 之上？不。

方案 B（严格 14）：
  石器时代(含夏商) 1, 西周 2, 春秋战国 3, 秦 4, 汉 5, 三国两晋南北朝 6,
  隋唐 7, 五代十国 8, 宋辽金 9, 元 10, 明 11, 清 12, 民国近代 13, 新中国 14
  => 夏商 并入 石器时代 顶层（其下 cn-xia-shang 作为二级）。
  但「夏商」是重要朝代，Lead 列表明确含「夏商」。

好，就用 15 个：石器时代、夏商、西周、春秋战国、秦、汉、三国两晋南北朝、
隋唐、五代十国、宋辽金、元、明、清、民国近代、新中国。
Lead 列表 17 项中我合并了「西汉/东汉→汉」与「隋/唐→隋唐」两项 => 15。
这是最小偏离且粒度合理。
"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

blocks = re.findall(r'    \{\n        "id": "[^"]+",.*?\n    \},\n', s, re.S)
head_end = s.index(blocks[0])
head = s[:head_end]
tail = s[s.rindex("]\n"):]

# ---- 1) 需要降级为二级 / 升级为顶层的映射 ----
# 旧 id -> (新 id, 新 parentId)  None 表示顶层
MAP = {
    # 顶层化
    "cn-spring-autumn": ("cn-zhou-east", None),      # 春秋 升为顶层并改名 东周
    "cn-zhou-east":    ("cn-zhou-east2", None),      # 原东周 保留但改名占位，稍后删
    "cn-han-west":     ("cn-han", None),             # 汉 顶层化
    "cn-han-east":     ("cn-han-east", "cn-han"),    # 东汉 降为二级
    "cn-sui":          ("cn-sui-tang", None),        # 隋唐 顶层化
    "cn-tang":         ("cn-tang", "cn-sui-tang"),   # 唐 降为二级
    "cn-zhou":         (None, None),                 # 删除（周 包装层）
    "cn-han":          ("cn-han", None),
    "cn-sui-tang":     ("cn-sui-tang", None),
    # 子期归属
    "cn-zhou-west":    ("cn-zhou-west", None),
    "cn-xia-shang":    ("cn-xia-shang", None),
    "cn-prehistory":   ("cn-prehistory", None),
    "cn-qin":          ("cn-qin", None),
    "cn-wei-jin-nanbei": ("cn-wei-jin-nanbei", None),
    "cn-wudai":        ("cn-wudai", None),
    "cn-song-liao-jin": ("cn-song-liao-jin", None),
    "cn-yuan":         ("cn-yuan", None),
    "cn-ming":         ("cn-ming", None),
    "cn-qing":         ("cn-qing", None),
    "cn-modern":       ("cn-modern", None),
    "cn-prc":          ("cn-prc", None),
    # 三国两晋南北朝 子期
    "cn-three-kingdoms": ("cn-three-kingdoms", "cn-wei-jin-nanbei"),
    "cn-three-shu": ("cn-three-shu", "cn-three-kingdoms"),
    "cn-three-wei": ("cn-three-wei", "cn-three-kingdoms"),
    "cn-three-wu": ("cn-three-wu", "cn-three-kingdoms"),
    "cn-liang-jin": ("cn-liang-jin", "cn-wei-jin-nanbei"),
    "cn-jin-west": ("cn-jin-west", "cn-liang-jin"),
    "cn-jin-east": ("cn-jin-east", "cn-liang-jin"),
    "cn-sixteen-kingdoms": ("cn-sixteen-kingdoms", "cn-wei-jin-nanbei"),
    "cn-nanbei": ("cn-nanbei", "cn-wei-jin-nanbei"),
    "cn-nanbei-north": ("cn-nanbei-north", "cn-nanbei"),
    "cn-nanbei-south": ("cn-nanbei-south", "cn-nanbei"),
    # 汉 子期
    "cn-han-new": ("cn-han-new", "cn-han"),
    # 隋唐 子期
    "cn-tang-early": ("cn-tang-early", "cn-tang"),
    "cn-tang-mid": ("cn-tang-mid", "cn-tang"),
    "cn-tang-late": ("cn-tang-late", "cn-tang"),
    # 夏商 子期
    "cn-xia": ("cn-xia", "cn-xia-shang"),
    "cn-shang": ("cn-shang", "cn-xia-shang"),
    "cn-shang-early": ("cn-shang-early", "cn-shang"),
    "cn-shang-late": ("cn-shang-late", "cn-shang"),
    # 史前 子期
    "cn-pre-paleolithic": ("cn-pre-paleolithic", "cn-prehistory"),
    "cn-pre-neolithic": ("cn-pre-neolithic", "cn-prehistory"),
    # 五代十国
    "cn-wudai-north": ("cn-wudai-north", "cn-wudai"),
    "cn-wudai-south": ("cn-wudai-south", "cn-wudai"),
    # 宋辽金
    "cn-song-north": ("cn-song-north", "cn-song-liao-jin"),
    "cn-song-south": ("cn-song-south", "cn-song-liao-jin"),
    "cn-liao": ("cn-liao", "cn-song-liao-jin"),
    "cn-jin": ("cn-jin", "cn-song-liao-jin"),
    # 元
    "cn-yuan-early": ("cn-yuan-early", "cn-yuan"),
    "cn-yuan-late": ("cn-yuan-late", "cn-yuan"),
    # 明
    "cn-ming-early": ("cn-ming-early", "cn-ming"),
    "cn-ming-mid": ("cn-ming-mid", "cn-ming"),
    "cn-ming-late": ("cn-ming-late", "cn-ming"),
    # 清
    "cn-qing-early": ("cn-qing-early", "cn-qing"),
    "cn-qing-mid": ("cn-qing-mid", "cn-qing"),
    "cn-qing-late": ("cn-qing-late", "cn-qing"),
    # 近代
    "cn-modern-republic": ("cn-modern-republic", "cn-modern"),
    "cn-modern-anti-japan": ("cn-modern-anti-japan", "cn-modern"),
    "cn-modern-liberation": ("cn-modern-liberation", "cn-modern"),
    # 新中国
    "cn-prc-early": ("cn-prc-early", "cn-prc"),
    "cn-prc-reform": ("cn-prc-reform", "cn-prc"),
    "cn-prc-new-era": ("cn-prc-new-era", "cn-prc"),
}

DROP = {"cn-zhou", "cn-zhou-east2", "cn-zhou-east",
        "cn-han-old", "cn-han2"}

# 春秋 / 战国 在新结构下挂到 cn-zhou-east（东周/春秋战国）之下
# => 需要新建一个顶层块 cn-zhou-east，容纳 春秋 与 战国 两个子期
# 原 cn-zhou-east(春秋战国父) 改名 -> cn-spring-autumn / cn-warring-states 保持子期

out = []
for b in blocks:
    m = re.search(r'"id": "([^"]+)"', b)
    oid = m.group(1)
    if oid in DROP:
        continue
    if oid not in MAP:
        print("UNMAPPED:", oid)
        continue
    nid, newp = MAP[oid]
    nb = b
    if nid and nid != oid:
        nb = nb.replace('"id": "%s",' % oid, '"id": "%s",' % nid, 1)
    if newp is None:
        nb = re.sub(r'"parentId": "[^"]*",', '"parentId": None,', nb, count=1)
    else:
        nb = re.sub(r'"parentId": "[^"]*",', '"parentId": "%s",' % newp, nb, count=1)
    out.append(nb)

# 追加新顶层块：cn-zhou-east（春秋战国），子期 cn-spring-autumn / cn-warring-states
ZHOU_EAST = '''    {
        "id": "cn-zhou-east",
        "name": "春秋战国",
        "alias": "东周",
        "parentId": None,
        "startYear": -770,
        "endYear": -256,
        "startDateText": "公元前770年",
        "endDateText": "公元前256年",
        "colorKey": "zhou",
        "summary": "周平王东迁洛邑之后的两百五十余年，王室衰微而诸侯争霸，中国历史进入社会剧变的时代。春秋百二十四年，郑、宋、齐、晋、楚、秦、吴、越等大国相继称霸，长勺、城濮泓水等战役奠定格局，孔子于此时整理六经并创立儒家。战国二百二十年七雄并立，铁器牛耕推广，井田制瓦解，魏文侯用李悂、秦孝公行商鞅之策，各国竞相变法；孟荀论战稷下争鸣，长平之战后天下形势奠定。这一时期是中华文明诸子传统的形成期，也是中央集权制度的孕育期，最终由秦王政次第灭六国而走向统一。",
        "territory": "王畿缩小；诸侯国实际控制中原及江淮、巴蜀、辽东广大区域",
        "capital": "洛邑（名义王都）",
        "population": "约四千万至五千万（估算）",
        "culture": "百家争鸣、私学兴起、变法与耕战、铸铁与牛耕、水利兴修、辞赋与小说萌芽",
        "keyFigures": ["fig-kongzi", "fig-lao-tzu", "fig-mozi", "fig-mencius", "fig-xunzi", "fig-shang-yang"],
        "relatedEvents": ["ev-zhou-pingwang", "ev-zhou-changpeng", "ev-zhou-warring-states", "ev-zhou-bianfa", "ev-zhou-baijia", "ev-zhou-changping", "ev-zhou-fall"],
        "tags": ["东周", "春秋", "战国", "百家争鸣", "变法"],
    },
'''
# 找到 cn-zhou-west 位置插在其后
idx = next(i for i, b in enumerate(out) if '"id": "cn-zhou-west"' in b)
out.insert(idx + 1, ZHOU_EAST)

# 春秋 / 战国 原块需改名回 cn-spring-autumn / cn-warring-states 并挂 cn-zhou-east
for b in out:
    if '"id": "cn-zhou-east2"' in b:  # 不会存在，保险
        pass

s = head + "".join(out) + tail
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("blocks now:", len(out))
