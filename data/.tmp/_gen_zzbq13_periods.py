# -*- coding: utf-8 -*-
"""v2.0.0 批次1：新建 4 个区域编年时期。

动机：世界史有 13 个近现代非西方人物**无时期可挂**——
印度民族运动、拉美独立、近代非洲、近代东南亚的区间空白。
不先建时期，这批人会被 reassign_figures.py 按生卒年挪到欧美主导的时期。

新建：
  w-modern-south-asia       近代南亚        1857-1947
  w-latin-america           拉丁美洲        1800-2026
  w-modern-africa           近代非洲        1600-1960
  w-modern-southeast-asia   近代东南亚      1800-1945

设计依据（照现有区域时期约定）：
  - 均为顶层时期（parentId: null）
  - tags 含「区域专题」→ App 的 splitByChronology 会归入补充组
  - colorKey 取现有枚举内最贴合者（india / earlymodern / medieval）

★ 必须同步更新 tools/reassign_figures.py 的 GROUP["world"]，
  否则这些时期不在候选池，人物永远归不进去。
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


periods = [
    {
        "id": "w-modern-south-asia",
        "name": "近代南亚",
        "alias": "英属印度与民族独立运动",
        "parentId": None,
        "startYear": 1857,
        "endYear": 1947,
        "startDateText": "公元1857年",
        "endDateText": "公元1947年",
        "colorKey": "india",
        "summary": "印度民族大起义后英国改行直辖，民族意识觉醒，国大党与穆斯林联盟兴起，1947年印巴分治独立。",
        "territory": "印度次大陆（今印度、巴基斯坦、孟加拉国）",
        "capital": "加尔各答、德里",
        "population": "约3亿至4亿",
        "culture": "英语教育、印刷资本主义、宗教改革与民族主义",
        "keyFigures": [],
        "relatedEvents": [],
        "tags": ["南亚", "印度", "民族独立", "英属印度", "区域专题"],
    },
    {
        "id": "w-latin-america",
        "name": "拉丁美洲",
        "alias": "拉美独立与现当代",
        "parentId": None,
        "startYear": 1800,
        "endYear": 2026,
        "startDateText": "公元1800年",
        "endDateText": "公元2026年",
        "colorKey": "earlymodern",
        "summary": "拉美各国自西葡独立后，历经考迪罗政治、出口经济、民粹与军政府、民主化浪潮，形成独特的混血文化。",
        "territory": "墨西哥至南美南端",
        "capital": "墨西哥城、布宜诺斯艾利斯、里约热内卢",
        "population": "约6.5亿",
        "culture": "混血文化、天主教、魔幻现实主义文学、足球",
        "keyFigures": [],
        "relatedEvents": [],
        "tags": ["拉丁美洲", "独立运动", "考迪罗", "区域专题"],
    },
    {
        "id": "w-modern-africa",
        "name": "近代非洲",
        "alias": "殖民瓜分与独立浪潮",
        "parentId": None,
        "startYear": 1600,
        "endYear": 1960,
        "startDateText": "公元1600年",
        "endDateText": "公元1960年",
        "colorKey": "medieval",
        "summary": "大西洋奴隶贸易、欧洲殖民瓜分、反殖民抗争，直至1960年「非洲年」十七国独立，殖民体系瓦解。",
        "territory": "非洲大陆",
        "capital": "—",
        "population": "约1亿至2.8亿",
        "culture": "奴隶贸易创伤、基督教与伊斯兰扩张、泛非主义",
        "keyFigures": [],
        "relatedEvents": [],
        "tags": ["非洲", "殖民", "奴隶贸易", "独立", "区域专题"],
    },
    {
        "id": "w-modern-southeast-asia",
        "name": "近代东南亚",
        "alias": "殖民统治与民族独立",
        "parentId": None,
        "startYear": 1800,
        "endYear": 1945,
        "startDateText": "公元1800年",
        "endDateText": "公元1945年",
        "colorKey": "earlymodern",
        "summary": "东南亚被英、法、荷、西、美瓜分为殖民地，暹罗以改革保持独立，民族主义兴起并走向战后独立。",
        "territory": "中南半岛与马来群岛",
        "capital": "曼谷、马尼拉、巴达维亚、西贡",
        "population": "约5000万至1.5亿",
        "culture": "殖民经济、华人移民、佛教与伊斯兰复兴、民族主义",
        "keyFigures": [],
        "relatedEvents": [],
        "tags": ["东南亚", "殖民", "暹罗", "民族主义", "区域专题"],
    },
]


if __name__ == "__main__":
    with io.open(os.path.join(HERE, "world_periods_zzbq13.json"), "w", encoding="utf-8") as f:
        json.dump(periods, f, ensure_ascii=False, indent=1)
    print("写出时期", len(periods), "个")
