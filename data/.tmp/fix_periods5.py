# -*- coding: utf-8 -*-
"""按 Lead 要求调整 periods：
1. 顶层区间严格首尾相接、互不重叠
2. cn-han-new -> cn-wangmang
3. 顶层 tags 加 "编年主干"
4. 顶层 relatedEvents 补足 4-6 条
"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

# ---- 1. 顶层区间调整为严格首尾相接 ----
TOP_YEARS = {
    "cn-prehistory":   (-3000000, -2070, "公元前300万年", "公元前2070年"),
    "cn-xia-shang":   (-2070, -1046, "公元前2070年", "公元前1046年"),
    "cn-zhou-west":   (-1046, -771, "公元前1046年", "公元前771年"),
    "cn-zhou-east":   (-771, -222, "公元前771年", "公元前222年"),
    "cn-qin":         (-221, -207, "公元前221年", "公元前207年"),
    "cn-han":         (-206, 220, "公元前206年", "公元220年"),
    "cn-wei-jin-nanbei": (220, 589, "公元220年", "公元589年"),
    "cn-sui-tang":    (589, 907, "公元589年", "公元907年"),
    "cn-wudai":       (907, 960, "公元907年", "公元960年"),
    "cn-song-liao-jin": (960, 1270, "公元960年", "公元1270年"),
    "cn-yuan":        (1270, 1368, "公元1270年", "公元1368年"),
    "cn-ming":        (1368, 1644, "公元1368年", "公元1644年"),
    "cn-qing":        (1644, 1912, "公元1644年", "公元1912年"),
    "cn-modern":      (1912, 1949, "公元1912年", "公元1949年"),
    "cn-prc":         (1949, 2026, "公元1949年", "至今"),
}


def set_block_year(pid, sy, ey, sdt, edt):
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


for pid, (sy, ey, sdt, edt) in TOP_YEARS.items():
    set_block_year(pid, sy, ey, sdt, edt)

# ---- 2. cn-han-new -> cn-wangmang ----
s = s.replace('"id": "cn-han-new",', '"id": "cn-wangmang",')
s = s.replace('"parentId": "cn-han",\n        "startYear": 9,', '"parentId": "cn-han",\n        "startYear": 9,')

# ---- 3. 顶层 tags 加 编年主干；顶层 relatedEvents 补足 ----
TOP_TAGS = {
    "cn-prehistory": ["编年主干", "远古", "石器时代", "文明起源"],
    "cn-xia-shang": ["编年主干", "夏", "商", "甲骨文", "青铜时代", "信史"],
    "cn-zhou-west": ["编年主干", "西周", "分封", "宗法", "礼乐", "井田"],
    "cn-zhou-east": ["编年主干", "春秋", "战国", "百家争鸣", "变法"],
    "cn-qin": ["编年主干", "秦", "统一", "中央集权", "郡县制", "始皇"],
    "cn-han": ["编年主干", "汉", "独尊儒术", "丝绸之路", "造纸术", "统一多民族国家"],
    "cn-wei-jin-nanbei": ["编年主干", "三国", "两晋", "南北朝", "民族融合", "佛教", "门阀"],
    "cn-sui-tang": ["编年主干", "隋唐", "科举制", "贞观之治", "开元盛世", "丝绸之路", "诗国"],
    "cn-wudai": ["编年主干", "五代十国", "契丹", "后周世宗", "李煜", "分裂"],
    "cn-song-liao-jin": ["编年主干", "宋", "辽", "金", "宋词", "四大发明", "靖康之变"],
    "cn-yuan": ["编年主干", "元", "蒙古", "行省制度", "元曲", "大都", "欧亚交流"],
    "cn-ming": ["编年主干", "明", "郑和下西洋", "长城", "紫禁城", "阳明心学", "白银"],
    "cn-qing": ["编年主干", "清", "康乾盛世", "洋务运动", "太平天国", "辛亥革命"],
    "cn-modern": ["编年主干", "近代", "民国", "五四运动", "抗日战争", "解放战争"],
    "cn-prc": ["编年主干", "新中国", "改革开放", "两弹一星", "一国两制", "加入世贸", "航天"],
}

TOP_EVENTS = {
    "cn-prehistory": ["ev-pre-peking-man", "ev-pre-yangshao", "ev-pre-longshan", "ev-pre-liangzhu", "ev-pre-huangdi"],
    "cn-xia-shang": ["ev-shang-tang-founding", "ev-shang-pan-geng-move", "ev-shang-jiagu", "ev-shang-wuding", "ev-shang-fall"],
    "cn-zhou-west": ["ev-zhou-founding", "ev-zhou-fengjian", "ev-zhou-zhougong", "ev-zhou-liwang", "ev-zhou-guoren", "ev-zhou-fall"],
    "cn-zhou-east": ["ev-zhou-pingwang", "ev-zhou-changpeng", "ev-zhou-warring-states", "ev-zhou-bianfa", "ev-zhou-baijia", "ev-zhou-fall"],
    "cn-qin": ["ev-qin-unify", "ev-qin-emperor-system", "ev-qin-county-system", "ev-qin-standardize", "ev-qin-burn-books", "ev-qin-fall"],
    "cn-han": ["ev-han-founding", "ev-han-wudi", "ev-han-zhangqian", "ev-han-siluroad", "ev-han-wangmang", "ev-han-yellow-turban", "ev-han-fall"],
    "cn-wei-jin-nanbei": ["ev-weijin-red-cliffs", "ev-weijin-eight-princes", "ev-weijin-yongjia", "ev-weijin-feishui", "ev-weijin-northern-wei", "ev-weijin-xiaowen-hanization", "ev-weijin-sui-unify"],
    "cn-sui-tang": ["ev-suita-sui-founding", "ev-suita-kemu", "ev-suita-grand-canal", "ev-tang-zhenguan", "ev-tang-kaiyuan", "ev-tang-anlushan", "ev-tang-fall"],
    "cn-wudai": ["ev-wudai-liang", "ev-wudai-tang", "ev-wudai-jin", "ev-wudai-zhou", "ev-wudai-chao-liao", "ev-wudai-song-founding"],
    "cn-song-liao-jin": ["ev-song-founding", "ev-song-qinliang", "ev-song-liao-chanyuan", "ev-song-jingkang", "ev-song-kaixi", "ev-song-yashan"],
    "cn-yuan": ["ev-yuan-mongol-unify", "ev-yuan-founding", "ev-yuan-xing-sheng", "ev-yuan-dadu", "ev-yuan-miao", "ev-yuan-fall"],
    "cn-ming": ["ev-ming-founding", "ev-ming-yongle", "ev-ming-sea", "ev-ming-wangyangming", "ev-ming-yitiaobian", "ev-ming-fall"],
    "cn-qing": ["ev-qing-founding", "ev-qing-kangxi", "ev-qing-qianlong", "ev-qing-opium-war", "ev-qing-taiping", "ev-qing-yangwu", "ev-qing-xinhai"],
    "cn-modern": ["ev-modern-republic", "ev-modern-may-fourth", "ev-modern-communist-party", "ev-modern-japanese-aggression", "ev-modern-victory", "ev-modern-liberation"],
    "cn-prc": ["ev-prc-founding", "ev-prc-first-five-year", "ev-prc-two-bombs", "ev-prc-reform", "ev-prc-special-zones", "ev-prc-wto", "ev-prc-hong-kong"],
}


def set_tags_events(pid, tags, events):
    global s
    m = re.search(r'("id": "%s",.*?)(\n    \},)' % re.escape(pid), s, re.S)
    if not m:
        raise KeyError(pid)
    blk = m.group(0)
    nb = re.sub(r'"tags": \[[^\]]*\],',
                '"tags": %s,' % json_tags(tags), blk, count=1)
    nb = re.sub(r'"relatedEvents": \[[^\]]*\],',
                '"relatedEvents": %s,' % json_ev(events), nb, count=1)
    s = s[:m.start()] + nb + s[m.end():]


def json_tags(tags):
    return "[" + ", ".join('"%s"' % t for t in tags) + "]"


def json_ev(evs):
    return "[" + ", ".join('"%s"' % e for e in evs) + "]"


for pid in TOP_TAGS:
    set_tags_events(pid, TOP_TAGS[pid], TOP_EVENTS[pid])

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("periods adjusted")
