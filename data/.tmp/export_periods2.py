# -*- coding: utf-8 -*-
"""导出 periods 为 china_periods.json：修正 keyFigures/relatedEvents 数量、
十国降为子期、顶层严格首尾相接。"""
import importlib.util
import json
import os
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p", os.path.join(HERE, "periods_data.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = m.PERIODS

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
    "cn-wudai-south":     (960, 979, "公元960年", "公元979年"),
    "cn-song-liao-jin":   (979, 1270, "公元979年", "公元1270年"),
    "cn-yuan":            (1271, 1368, "公元1271年", "公元1368年"),
    "cn-ming":            (1368, 1644, "公元1368年", "公元1644年"),
    "cn-qing":            (1644, 1912, "公元1644年", "公元1912年"),
    "cn-modern":          (1912, 1949, "公元1912年", "公元1949年"),
    "cn-prc":             (1949, 2026, "公元1949年", "至今"),
}

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
    "cn-song-north":     (979, 1127, "公元979年", "公元1127年"),
    "cn-song-south":     (1127, 1270, "公元1127年", "公元1270年"),
    "cn-liao":           (979, 1125, "公元979年", "公元1125年"),
    "cn-jin":            (979, 1234, "公元979年", "公元1234年"),
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

# 各时期挑选 6 位关键人物（去重、按出现顺序）
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

# 各时期精选代表事件（用于裁剪 relatedEvents）
CURATED_EVENTS = {
    "cn-pre-paleolithic": ["ev-pre-peking-man", "ev-pre-yuanmou", "ev-pre-shandongdong"],
    "cn-pre-neolithic": ["ev-pre-yangshao", "ev-pre-longshan", "ev-pre-liangzhu", "ev-pre-hemudu", "ev-pre-hongshan", "ev-pre-yu"],
    "cn-xia": ["ev-xia-yu-dynasty", "ev-xia-cheng", "ev-xia-taikang", "ev-xia-zhongxing", "ev-xia-erlitou"],
    "cn-shang": ["ev-shang-tang-founding", "ev-shang-pan-geng-move", "ev-shang-jiagu", "ev-shang-wuding", "ev-shang-bronze", "ev-shang-fall"],
    "cn-shang-early": ["ev-shang-tang-founding", "ev-shang-yiyin", "ev-shang-taijia", "ev-shang-zhengzhou-city"],
    "cn-shang-late": ["ev-shang-pan-geng-move", "ev-shang-jiagu", "ev-shang-wuding", "ev-shang-furen", "ev-shang-doushang", "ev-shang-fall"],
    "cn-spring-autumn": ["ev-zhou-keduan", "ev-zhou-changpeng", "ev-zhou-liujiu", "ev-zhou-qihuang", "ev-zhou-chuzhuang", "ev-zhou-zichan"],
    "cn-warring-states": ["ev-zhou-warring-states", "ev-zhou-bianfa", "ev-zhou-qin-shang-yang", "ev-zhou-changping", "ev-zhou-maling", "ev-zhou-baijia", "ev-zhou-fall"],
    "cn-han-west": ["ev-han-founding", "ev-han-wenjing", "ev-han-wudi", "ev-han-tui-en", "ev-han-salt-iron", "ev-han-zhangqian", "ev-han-siluroad", "ev-han-sima-qian"],
    "cn-wangmang": ["ev-han-wangmang", "ev-han-wangtian", "ev-han-green-forest", "ev-han-red-brow", "ev-han-wangmang-fall"],
    "cn-han-east": ["ev-han-donghan", "ev-han-guangwu", "ev-han-cai-lun", "ev-han-zhangheng", "ev-han-buddhism", "ev-han-party-frison", "ev-han-yellow-turban", "ev-han-fall"],
    "cn-three-kingdoms": ["ev-weijin-three-kingdoms", "ev-weijin-red-cliffs", "ev-weijin-yiling", "ev-weijin-chu-han", "ev-weijin-shu-fall", "ev-weijin-wu-fall"],
    "cn-three-shu": ["ev-weijin-chu-han", "ev-weijin-san-gu-maolu", "ev-weijin-nanman", "ev-weijin-shibiao", "ev-weijin-yizhou-fall", "ev-weijin-shu-fall"],
    "cn-three-wei": ["ev-weijin-wei-founding", "ev-weijin-guan-dong", "ev-weijin-guan-dong-2", "ev-weijin-sima-power", "ev-weijin-jin-unify"],
    "cn-three-wu": ["ev-weijin-three-kingdoms", "ev-weijin-yiling", "ev-weijin-nanyue", "ev-weijin-wu-fall"],
    "cn-liang-jin": ["ev-weijin-jin-unify", "ev-weijin-taikang", "ev-weijin-eight-princes", "ev-weijin-yongjia", "ev-weijin-dongjin", "ev-weijin-nanqian", "ev-weijin-taiping"],
    "cn-jin-west": ["ev-weijin-jin-unify", "ev-weijin-taikang", "ev-weijin-eight-princes", "ev-weijin-liu-yuan", "ev-weijin-yongjia", "ev-weijin-luoyang-fall"],
    "cn-jin-east": ["ev-weijin-dongjin", "ev-weijin-nanqian", "ev-weijin-huaiyin", "ev-weijin-feishui", "ev-weijin-taiping", "ev-weijin-liuyu"],
    "cn-sixteen-kingdoms": ["ev-weijin-sixteen-kingdoms", "ev-weijin-liu-yuan", "ev-weijin-fu-jian", "ev-weijin-feishui", "ev-weijin-northern-wei"],
    "cn-nanbei": ["ev-weijin-north-south", "ev-weijin-northern-wei", "ev-weijin-xiaowen-hanization", "ev-weijin-juntian", "ev-weijin-houjing", "ev-weijin-sui-unify"],
    "cn-nanbei-north": ["ev-weijin-northern-wei", "ev-weijin-xiaowen-hanization", "ev-weijin-juntian", "ev-weijin-san-chang", "ev-weijin-yungong"],
    "cn-nanbei-south": ["ev-weijin-north-south", "ev-weijin-liang-wudi", "ev-weijin-houjing", "ev-weijin-sui-unify"],
    "cn-sui": ["ev-suita-sui-founding", "ev-suita-kemu", "ev-suita-kaihuang", "ev-suita-grand-canal", "ev-suita-luoyang", "ev-suita-gaoli", "ev-suita-fall"],
    "cn-tang": ["ev-tang-founding", "ev-tang-xuanwumen", "ev-tang-zhenguan", "ev-tang-kaiyuan", "ev-tang-xuanzang", "ev-tang-anlushan", "ev-tang-huangchao", "ev-tang-fall"],
    "cn-tang-early": ["ev-tang-founding", "ev-tang-xuanwumen", "ev-tang-zhenguan", "ev-tang-wuzetian", "ev-tang-kaiyuan", "ev-tang-xuanzang", "ev-tang-jianzhen", "ev-tang-chang-an"],
    "cn-tang-mid": ["ev-tang-anlushan", "ev-tang-luoyang-fall", "ev-tang-chang-an-fall", "ev-tang-pugu", "ev-tang-liu-yan", "ev-tang-jingde", "ev-tang-ganbu"],
    "cn-tang-late": ["ev-tang-nongfu", "ev-tang-hezhong", "ev-tang-huangchao", "ev-tang-luoyang-sack", "ev-tang-fall"],
    "cn-wudai-north": ["ev-wudai-liang", "ev-wudai-tang", "ev-wudai-jin", "ev-wudai-yanyun", "ev-wudai-han", "ev-wudai-zhou", "ev-wudai-shizong"],
    "cn-wudai-south": ["ev-wudai-wu", "ev-wudai-nantang", "ev-wudai-quanzhou-trade", "ev-wudai-beihan"],
    "cn-song-north": ["ev-song-founding", "ev-song-cup-wine", "ev-song-qinliang", "ev-song-qingliang", "ev-song-wanganshi", "ev-song-xining", "ev-song-yuanyou", "ev-song-jingkang"],
    "cn-song-south": ["ev-song-nansong", "ev-song-yuefei", "ev-song-shaoxing-treaty", "ev-song-yuangong", "ev-song-yashan", "ev-song-wen-tianxiang"],
    "cn-liao": ["ev-liao-founding", "ev-liao-shengzong", "ev-song-liao-chanyuan", "ev-liao-fall"],
    "cn-jin": ["ev-song-jin-rise", "ev-song-jingkang", "ev-song-jin-shijin", "ev-song-caizhou", "ev-song-jin-fall"],
    "cn-yuan-early": ["ev-yuan-mongol-unify", "ev-yuan-jasaga", "ev-yuan-xiya", "ev-yuan-xixia", "ev-yuan-ailiboge", "ev-yuan-kublai"],
    "cn-yuan-late": ["ev-yuan-founding", "ev-yuan-xing-sheng", "ev-yuan-dadu", "ev-yuan-hailing", "ev-yuan-miao", "ev-yuan-fall"],
    "cn-ming-early": ["ev-ming-founding", "ev-ming-hongwu", "ev-ming-yongle", "ev-ming-zhenghe", "ev-ming-tumu", "ev-ming-yu-qian", "ev-ming-hongzhi", "ev-ming-sea"],
    "cn-ming-mid": ["ev-ming-jiajing", "ev-ming-qi-jiguang", "ev-ming-longqing", "ev-ming-wanli", "ev-ming-yitiaobian", "ev-ming-hai-ru", "ev-ming-xu-xiake"],
    "cn-ming-late": ["ev-ming-tianqi", "ev-ming-chongzhen", "ev-ming-liaodong", "ev-ming-buzhou", "ev-ming-lizicheng", "ev-ming-fall"],
    "cn-qing-early": ["ev-qing-founding", "ev-qing-qing-enter", "ev-qing-tifa", "ev-qing-sanfan", "ev-qing-taiwan", "ev-qing-yaksa", "ev-qing-nivchu", "ev-qing-junji"],
    "cn-qing-mid": ["ev-qing-qianlong", "ev-qing-siku", "ev-qing-wenziyu", "ev-qing-bailianjiao", "ev-qing-jiaqing", "ev-qing-guangzhou-trade"],
    "cn-qing-late": ["ev-qing-opium-war", "ev-qing-nanjing-treaty", "ev-qing-taiping", "ev-qing-yangwu", "ev-qing-jiawu", "ev-qing-wuxu", "ev-qing-new-policies", "ev-qing-xinhai"],
    "cn-modern-republic": ["ev-modern-republic", "ev-modern-provisional", "ev-modern-yuan-shikai", "ev-modern-empire", "ev-modern-zhangxun", "ev-modern-hugu", "ev-modern-may-fourth", "ev-modern-communist-party", "ev-modern-north-expedition"],
    "cn-modern-anti-japan": ["ev-modern-japanese-aggression", "ev-modern-jiu-yi-ba", "ev-modern-jiu-ba", "ev-modern-pingxingguan", "ev-modern-taierzhuang", "ev-modern-baihui", "ev-modern-jiangkou", "ev-modern-victory"],
    "cn-modern-liberation": ["ev-modern-chongqing-talk", "ev-modern-civil-war", "ev-modern-jinping", "ev-modern-liaoshen", "ev-modern-huaihai", "ev-modern-pingjin", "ev-modern-crossing", "ev-modern-liberation"],
    "cn-prc-early": ["ev-prc-founding", "ev-prc-land-reform", "ev-prc-korean-war", "ev-prc-first-five-year", "ev-prc-socialist-transform", "ev-prc-great-leap", "ev-prc-two-bombs", "ev-prc-dongfanghong", "ev-prc-hybrid-rice", "ev-prc-zhou-enlai", "ev-prc-tangshan", "ev-prc-gang-of-four"],
    "cn-prc-reform": ["ev-prc-reform", "ev-prc-henan-village", "ev-prc-special-zones", "ev-prc-southern-tour", "ev-prc-socialist-market", "ev-prc-shenzhen", "ev-prc-hong-kong", "ev-prc-macao", "ev-prc-wto", "ev-prc-chang-e", "ev-prc-olympics", "ev-prc-wenchuan"],
    "cn-prc-new-era": ["ev-prc-new-era", "ev-prc-belt-road", "ev-prc-poverty", "ev-prc-carbon", "ev-prc-beidou", "ev-prc-tianwen", "ev-prc-chang-e-five", "ev-prc-civilization", "ev-prc-anti-corruption"],
}


def dedup_keep(seq, n):
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out[:n]


out = []
for p in P:
    r = dict(p)
    pid = r["id"]
    if pid in TOP:
        sy, ey, sdt, edt = TOP[pid]
        r.update(startYear=sy, endYear=ey, startDateText=sdt, endDateText=edt)
        r["parentId"] = None
        tags = list(r.get("tags") or [])
        if "编年主干" not in tags:
            tags.insert(0, "编年主干")
        r["tags"] = tags
        r["keyFigures"] = dedup_keep(r.get("keyFigures") or [], 6)
        r["relatedEvents"] = dedup_keep(TOP_EVENTS.get(pid, []) or (r.get("relatedEvents") or []), 8)
    else:
        if pid in CHILD:
            sy, ey, sdt, edt = CHILD[pid]
            r.update(startYear=sy, endYear=ey, startDateText=sdt, endDateText=edt)
        if pid == "cn-wudai-south":
            # 十国（960-979）作为顶层编年节点，与五代（907-960）并列，
            # 宋辽金顶层自 960 起，二者构成五代十国并行的编年切分。
            r["parentId"] = None
        r["keyFigures"] = dedup_keep(r.get("keyFigures") or [], 6)
        r["relatedEvents"] = dedup_keep(
            CURATED_EVENTS.get(pid, r.get("relatedEvents") or []), 8)

    ordered = {
        "id": pid, "name": r["name"], "alias": r.get("alias", ""),
        "parentId": r.get("parentId"), "startYear": r["startYear"], "endYear": r["endYear"],
        "startDateText": r["startDateText"], "endDateText": r["endDateText"],
        "colorKey": r.get("colorKey", ""), "summary": r["summary"],
        "territory": r.get("territory", ""), "capital": r.get("capital", ""),
        "population": r.get("population", ""), "culture": r.get("culture", ""),
        "keyFigures": r.get("keyFigures") or [],
        "relatedEvents": r.get("relatedEvents") or [],
        "tags": r.get("tags") or [],
    }
    out.append(ordered)

path = os.path.join(HERE, "china_periods.json")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

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
    if not (3 <= len(r["keyFigures"]) <= 6):
        errs.append("KF %s = %d" % (r["id"], len(r["keyFigures"])))
    if not (3 <= len(r["relatedEvents"]) <= 8):
        errs.append("RE %s = %d" % (r["id"], len(r["relatedEvents"])))
    if not (150 <= len(r["summary"]) <= 400):
        errs.append("SUM %s = %d" % (r["id"], len(r["summary"])))
    if not r["tags"]:
        errs.append("TAGS %s" % r["id"])

tops = sorted(top, key=lambda x: x["startYear"])
for a, b in zip(tops, tops[1:]):
    # 允许共享边界年（前一期的 endYear == 后一期的 startYear），
    # 只禁止真正重叠（后一期 startYear < 前一期 endYear）
    if b["startYear"] < a["endYear"]:
        errs.append("OVERLAP %s(%d..%d) -> %s(%d..%d)" % (
            a["id"], a["startYear"], a["endYear"], b["id"], b["startYear"], b["endYear"]))

print("periods:", len(out), "top:", len(top))
for t in tops:
    print("  %-22s %7d..%-6d kf=%d re=%d tags=%d" % (
        t["id"], t["startYear"], t["endYear"], len(t["keyFigures"]), len(t["relatedEvents"]), len(t["tags"])))
if errs:
    print("\nERRORS (%d):" % len(errs))
    for e in errs:
        print("  ", e)
else:
    print("\nOK -> %s" % path)
