# -*- coding: utf-8 -*-
"""导出 periods 为 data/.tmp/china_periods.json，并按 Lead 指定区间修正顶层。"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p", os.path.join(HERE, "periods_data.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = m.PERIODS

# ---- Lead 指定的顶层区间（严格首尾相接） ----
TOP = {
    "cn-prehistory":       (-3000000, -2070, "公元前300万年", "公元前2070年"),
    "cn-xia-shang":       (-2070, -1046, "公元前2070年", "公元前1046年"),
    "cn-zhou-west":       (-1046, -771, "公元前1046年", "公元前771年"),
    "cn-zhou-east":       (-771, -222, "公元前771年", "公元前222年"),
    "cn-qin":             (-221, -207, "公元前221年", "公元前207年"),
    "cn-han":             (-206, 220, "公元前206年", "公元220年"),
    "cn-wei-jin-nanbei":  (220, 589, "公元220年", "公元589年"),
    "cn-sui-tang":        (589, 907, "公元589年", "公元907年"),
    "cn-wudai":           (907, 960, "公元907年", "公元960年"),
    "cn-song-liao-jin":   (960, 1270, "公元960年", "公元1270年"),
    "cn-yuan":            (1271, 1368, "公元1271年", "公元1368年"),
    "cn-ming":            (1368, 1644, "公元1368年", "公元1644年"),
    "cn-qing":            (1644, 1912, "公元1644年", "公元1912年"),
    "cn-modern":          (1912, 1949, "公元1912年", "公元1949年"),
    "cn-prc":             (1949, 2026, "公元1949年", "至今"),
}

# ---- 子期区间（须落在父期内） ----
CHILD = {
    "cn-pre-paleolithic": (-3000000, -12000, "公元前300万年", "公元前12000年"),
    "cn-pre-neolithic":   (-12000, -2070, "公元前12000年", "公元前2070年"),
    "cn-xia":            (-2070, -1600, "公元前2070年", "公元前1600年"),
    "cn-shang":          (-1600, -1046, "公元前1600年", "公元前1046年"),
    "cn-shang-early":    (-1600, -1300, "公元前1600年", "公元前1300年"),
    "cn-shang-late":     (-1300, -1046, "公元前1300年", "公元前1046年"),
    "cn-spring-autumn":  (-771, -476, "公元前771年", "公元前476年"),
    "cn-warring-states": (-475, -222, "公元前475年", "公元前222年"),
    "cn-han-west":       (-206, 9, "公元前206年", "公元9年"),
    "cn-wangmang":       (9, 23, "公元9年", "公元23年"),
    "cn-han-east":       (25, 220, "公元25年", "公元220年"),
    "cn-three-kingdoms": (220, 280, "公元220年", "公元280年"),
    "cn-three-shu":      (221, 263, "公元221年", "公元263年"),
    "cn-three-wei":      (220, 265, "公元220年", "公元265年"),
    "cn-three-wu":       (222, 280, "公元222年", "公元280年"),
    "cn-liang-jin":      (265, 420, "公元265年", "公元420年"),
    "cn-jin-west":       (265, 316, "公元265年", "公元316年"),
    "cn-jin-east":       (317, 420, "公元317年", "公元420年"),
    "cn-sixteen-kingdoms": (304, 439, "公元304年", "公元439年"),
    "cn-nanbei":         (386, 589, "公元386年", "公元589年"),
    "cn-nanbei-north":   (386, 581, "公元386年", "公元581年"),
    "cn-nanbei-south":   (420, 589, "公元420年", "公元589年"),
    "cn-sui":            (589, 618, "公元589年", "公元618年"),
    "cn-tang":           (618, 907, "公元618年", "公元907年"),
    "cn-tang-early":     (618, 755, "公元618年", "公元755年"),
    "cn-tang-mid":       (755, 827, "公元755年", "公元827年"),
    "cn-tang-late":      (827, 907, "公元827年", "公元907年"),
    "cn-wudai-north":    (907, 960, "公元907年", "公元960年"),
    "cn-wudai-south":    (960, 979, "公元960年", "公元979年"),
    "cn-song-north":     (960, 1127, "公元960年", "公元1127年"),
    "cn-song-south":     (1127, 1270, "公元1127年", "公元1270年"),
    "cn-liao":           (960, 1125, "公元960年", "公元1125年"),
    "cn-jin":            (1115, 1234, "公元1115年", "公元1234年"),
    "cn-yuan-early":     (1271, 1271, "公元1271年", "公元1271年"),
    "cn-yuan-late":      (1271, 1368, "公元1271年", "公元1368年"),
    "cn-ming-early":     (1368, 1521, "公元1368年", "公元1521年"),
    "cn-ming-mid":       (1521, 1620, "公元1521年", "公元1620年"),
    "cn-ming-late":      (1620, 1644, "公元1620年", "公元1644年"),
    "cn-qing-early":     (1644, 1735, "公元1644年", "公元1735年"),
    "cn-qing-mid":       (1735, 1820, "公元1735年", "公元1820年"),
    "cn-qing-late":      (1820, 1912, "公元1820年", "公元1912年"),
    "cn-modern-republic": (1912, 1927, "公元1912年", "公元1927年"),
    "cn-modern-anti-japan": (1931, 1945, "公元1931年", "公元1945年"),
    "cn-modern-liberation": (1945, 1949, "公元1945年", "公元1949年"),
    "cn-prc-early":      (1949, 1978, "公元1949年", "公元1978年"),
    "cn-prc-reform":     (1978, 2012, "公元1978年", "公元2012年"),
    "cn-prc-new-era":    (2012, 2026, "公元2012年", "至今"),
}

# ---- 顶层 tags 追加 编年主干；顶层 relatedEvents 补足 ----
TOP_EVENTS = {
    "cn-prehistory": ["ev-pre-peking-man", "ev-pre-yangshao", "ev-pre-longshan", "ev-pre-liangzhu", "ev-pre-huangdi"],
    "cn-xia-shang": ["ev-shang-tang-founding", "ev-shang-pan-geng-move", "ev-shang-jiagu", "ev-shang-wuding", "ev-shang-fall"],
    "cn-zhou-west": ["ev-zhou-founding", "ev-zhou-fengjian", "ev-zhou-zhougong", "ev-zhou-liwang", "ev-zhou-guoren", "ev-zhou-fall"],
    "cn-zhou-east": ["ev-zhou-pingwang", "ev-zhou-changpeng", "ev-zhou-warring-states", "ev-zhou-bianfa", "ev-zhou-baijia", "ev-zhou-fall"],
    "cn-qin": ["ev-qin-unify", "ev-qin-emperor-system", "ev-qin-county-system", "ev-qin-standardize", "ev-qin-burn-books", "ev-qin-fall"],
    "cn-han": ["ev-han-founding", "ev-han-wudi", "ev-han-zhangqian", "ev-han-siluroad", "ev-han-wangmang", "ev-han-yellow-turban", "ev-han-fall"],
    "cn-wei-jin-nanbei": ["ev-weijin-red-cliffs", "ev-weijin-eight-princes", "ev-weijin-yongjia", "ev-weijin-feishui", "ev-weijin-northern-wei", "ev-weijin-xiaowen-hanization", "ev-weijin-sui-unify"],
    "cn-sui-tang": ["ev-suita-sui-founding", "ev-suita-kemu", "ev-suita-grand-canal", "ev-tang-zhenguan", "ev-tang-kaiyuan", "ev-tang-anlushan", "ev-tang-fall"],
    "cn-wudai": ["ev-wudai-liang", "ev-wudai-tang", "ev-wudai-jin", "ev-wudai-zhou", "ev-wudai-song-founding"],
    "cn-song-liao-jin": ["ev-song-founding", "ev-song-qinliang", "ev-song-liao-chanyuan", "ev-song-jingkang", "ev-song-kaixi", "ev-song-yashan"],
    "cn-yuan": ["ev-yuan-mongol-unify", "ev-yuan-founding", "ev-yuan-xing-sheng", "ev-yuan-dadu", "ev-yuan-miao", "ev-yuan-fall"],
    "cn-ming": ["ev-ming-founding", "ev-ming-yongle", "ev-ming-sea", "ev-ming-wangyangming", "ev-ming-yitiaobian", "ev-ming-fall"],
    "cn-qing": ["ev-qing-founding", "ev-qing-kangxi", "ev-qing-qianlong", "ev-qing-opium-war", "ev-qing-taiping", "ev-qing-yangwu", "ev-qing-xinhai"],
    "cn-modern": ["ev-modern-republic", "ev-modern-may-fourth", "ev-modern-communist-party", "ev-modern-japanese-aggression", "ev-modern-victory", "ev-modern-liberation"],
    "cn-prc": ["ev-prc-founding", "ev-prc-first-five-year", "ev-prc-two-bombs", "ev-prc-reform", "ev-prc-special-zones", "ev-prc-wto", "ev-prc-hong-kong"],
}

out = []
for p in P:
    r = dict(p)
    if r["id"] in TOP:
        sy, ey, sdt, edt = TOP[r["id"]]
        r["startYear"], r["endYear"] = sy, ey
        r["startDateText"], r["endDateText"] = sdt, edt
        r["parentId"] = None
        tags = list(r.get("tags") or [])
        if "编年主干" not in tags:
            tags.insert(0, "编年主干")
        r["tags"] = tags
        evs = list(r.get("relatedEvents") or [])
        for e in TOP_EVENTS.get(r["id"], []):
            if e not in evs:
                evs.append(e)
        r["relatedEvents"] = evs[:8]
    elif r["id"] in CHILD:
        sy, ey, sdt, edt = CHILD[r["id"]]
        r["startYear"], r["endYear"] = sy, ey
        r["startDateText"], r["endDateText"] = sdt, edt
    # 规范字段顺序
    ordered = {
        "id": r["id"], "name": r["name"], "alias": r.get("alias", ""),
        "parentId": r.get("parentId"), "startYear": r["startYear"], "endYear": r["endYear"],
        "startDateText": r["startDateText"], "endDateText": r["endDateText"],
        "colorKey": r.get("colorKey", ""), "summary": r["summary"],
        "territory": r.get("territory", ""), "capital": r.get("capital", ""),
        "population": r.get("population", ""), "culture": r.get("culture", ""),
        "keyFigures": list(r.get("keyFigures") or []),
        "relatedEvents": list(r.get("relatedEvents") or []),
        "tags": list(r.get("tags") or []),
    }
    out.append(ordered)

path = os.path.join(HERE, "china_periods.json")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# 校验
ids = {r["id"] for r in out}
errs = []
top = [r for r in out if not r.get("parentId")]
for r in out:
    if r["startYear"] > r["endYear"]:
        errs.append("ORDER %s" % r["id"])
    if r.get("parentId"):
        p = next((x for x in out if x["id"] == r["parentId"]), None)
        if p is None:
            errs.append("NOPARENT %s" % r["id"])
        elif not (p["startYear"] <= r["startYear"] and r["endYear"] <= p["endYear"]):
            errs.append("RANGE %s [%d,%d] not in %s [%d,%d]" % (
                r["id"], r["startYear"], r["endYear"], p["id"], p["startYear"], p["endYear"]))
    if not (3 <= len(r.get("keyFigures") or []) <= 6):
        errs.append("KF %s = %d" % (r["id"], len(r.get("keyFigures") or [])))
    if not (3 <= len(r.get("relatedEvents") or []) <= 8):
        errs.append("RE %s = %d" % (r["id"], len(r.get("relatedEvents") or [])))
    if not (150 <= len(r["summary"]) <= 400):
        errs.append("SUM %s = %d" % (r["id"], len(r["summary"])))

# 顶层首尾相接
tops = sorted(top, key=lambda x: x["startYear"])
for a, b in zip(tops, tops[1:]):
    if b["startYear"] <= a["endYear"]:
        errs.append("OVERLAP %s(%d..%d) %s(%d..%d)" % (
            a["id"], a["startYear"], a["endYear"], b["id"], b["startYear"], b["endYear"]))

print("periods:", len(out), " top:", len(top))
for t in tops:
    print("  %-22s %6d..%-6d  tags=%d" % (t["id"], t["startYear"], t["endYear"], len(t["tags"])))
if errs:
    print("\nERRORS (%d):" % len(errs))
    for e in errs:
        print("  ", e)
else:
    print("\nOK -> %s" % path)
