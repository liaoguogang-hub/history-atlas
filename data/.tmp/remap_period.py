#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按年份把事件重新挂到合适的时期：优先保留原时期（若区间包含），
否则从候选列表中选一个区间包含该年的时期，否则选跨度最近且包含起始年的时期。"""
import json, sys, os

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(D, "world_periods.json"), encoding="utf-8"))
PM = {p["id"]: p for p in P}
IDS = list(PM.keys())

# 手工指定优先时期候选（按语义）
PREF = {
    "w-prehistory": ["w-prehistory", "w-paleolithic", "w-neolithic"],
    "w-neolithic": ["w-neolithic", "w-paleolithic", "w-prehistory"],
    "w-sumer": ["w-sumer", "w-ancient-near-east"],
    "w-ancient-near-east": ["w-ancient-near-east", "w-egypt-old", "w-sumer"],
    "w-old-babylon": ["w-old-babylon", "w-ancient-near-east"],
    "w-assyrian": ["w-assyrian", "w-ancient-near-east"],
    "w-neobabylonian": ["w-neobabylonian", "w-ancient-near-east"],
    "w-egypt-old": ["w-egypt-old", "w-ancient-near-east"],
    "w-near-east-persian": ["w-near-east-persian", "w-classical-greece", "w-hellenistic"],
    "w-archaic-greece": ["w-archaic-greece", "w-classical-greece"],
    "w-classical-age": ["w-classical-age", "w-classical-greece"],
    "w-hellenistic": ["w-hellenistic", "w-classical-greece", "w-macedonian"],
    "w-macedonian": ["w-macedonian", "w-hellenistic"],
    "w-roman-republic": ["w-roman-republic", "w-roman"],
    "w-roman-empire": ["w-roman-empire", "w-roman"],
    "w-late-roman": ["w-late-roman", "w-roman", "w-byzantium-early"],
    "w-byzantium-early": ["w-byzantium-early", "w-late-roman", "w-post-roman", "w-post-roman-europe"],
    "w-post-roman": ["w-post-roman", "w-post-roman-europe", "w-post-roman-asia", "w-abbasid-golden", "w-carolingian"],
    "w-punic-war": ["w-punic-war", "w-roman-republic"],
    "w-indus": ["w-indus", "w-ancient-south-asia"],
    "w-aryan": ["w-aryan", "w-ancient-south-asia"],
    "w-maurya": ["w-maurya", "w-ancient-south-asia"],
    "w-minoan": ["w-minoan", "w-mycenaean"],
    "w-mycenaean": ["w-mycenaean", "w-minoan"],
    "w-roman": ["w-roman-republic", "w-roman-empire", "w-late-roman", "w-roman", "w-byzantium-early", "w-post-roman"],
    "w-classical-greece": ["w-classical-age", "w-archaic-greece", "w-hellenistic", "w-classical-greece", "w-macedonian", "w-punic-war", "w-near-east-persian"],
    "w-ancient-south-asia": ["w-indus", "w-aryan", "w-maurya", "w-ancient-south-asia"],
    "w-america-precol": ["w-maya", "w-mesoamerica", "w-andes", "w-america-precol"],
    "w-andes": ["w-andes", "w-america-precol"],
    "w-maya": ["w-maya", "w-america-precol"],
    "w-mesoamerica": ["w-mesoamerica", "w-america-precol"],
    "w-africa-west": ["w-africa-west", "w-old-world", "w-post-roman", "w-medieval-islam"],
    "w-africa-east": ["w-africa-east", "w-old-world", "w-post-roman", "w-medieval-islam"],
    "w-old-world": ["w-old-world", "w-africa-west", "w-africa-east", "w-post-roman"],
    "w-medieval": ["w-medieval-china", "w-medieval-islam", "w-byzantium", "w-crusades", "w-mongol-empire", "w-medieval"],
    "w-medieval-china": ["w-medieval-china", "w-tang-song", "w-cn-song", "w-medieval"],
    "w-medieval-islam": ["w-medieval-islam", "w-abbasid-golden", "w-islamic-golden", "w-medieval", "w-post-roman"],
    "w-abbasid-golden": ["w-abbasid-golden", "w-islamic-golden", "w-medieval-islam", "w-post-roman"],
    "w-islamic-golden": ["w-islamic-golden", "w-abbasid-golden", "w-post-roman"],
    "w-early-islam": ["w-early-islam", "w-post-roman", "w-abbasid-golden"],
    "w-post-roman-europe": ["w-post-roman-europe", "w-carolingian", "w-post-roman", "w-post-roman-asia"],
    "w-carolingian": ["w-carolingian", "w-post-roman-europe", "w-post-roman"],
    "w-post-roman-asia": ["w-post-roman-asia", "w-cn-tang", "w-tang-song", "w-post-roman", "w-medieval-china"],
    "w-tang-song": ["w-tang-song", "w-cn-song", "w-medieval-china", "w-post-roman-asia"],
    "w-cn-han": ["w-cn-han", "w-han-tang", "w-ancient-china"],
    "w-cn-tang": ["w-cn-tang", "w-han-tang", "w-tang-song", "w-post-roman-asia"],
    "w-cn-song": ["w-cn-song", "w-tang-song", "w-medieval-china"],
    "w-cn-ming": ["w-cn-ming", "w-ming-qing", "w-renaissance"],
    "w-cn-qing": ["w-cn-qing", "w-ming-qing", "w-imperialism", "w-modern"],
    "w-ming-qing": ["w-ming-qing", "w-cn-ming", "w-cn-qing", "w-early-modern"],
    "w-renaissance": ["w-italian-renaissance", "w-northern-renaissance", "w-byzantium-late", "w-renaissance"],
    "w-italian-renaissance": ["w-italian-renaissance", "w-renaissance"],
    "w-northern-renaissance": ["w-northern-renaissance", "w-renaissance"],
    "w-byzantium-late": ["w-byzantium-late", "w-renaissance", "w-medieval"],
    "w-byzantium": ["w-byzantium", "w-medieval"],
    "w-crusades": ["w-crusades", "w-medieval", "w-medieval-islam"],
    "w-mongol-empire": ["w-mongol-empire", "w-medieval", "w-medieval-china", "w-medieval-islam"],
    "w-early-modern": ["w-age-of-sail", "w-scientific-revolution", "w-absolute-monarchy", "w-early-modern", "w-southeast-asia", "w-oceania"],
    "w-age-of-sail": ["w-age-of-sail", "w-early-modern"],
    "w-scientific-revolution": ["w-scientific-revolution", "w-early-modern"],
    "w-absolute-monarchy": ["w-absolute-monarchy", "w-early-modern"],
    "w-modern": ["w-industrial-rev", "w-imperialism", "w-modern"],
    "w-industrial-rev": ["w-industrial-rev", "w-modern"],
    "w-imperialism": ["w-imperialism", "w-modern"],
    "w-world-wars": ["w-world-wars", "w-contemporary", "w-cold-war"],
    "w-contemporary": ["w-cold-war", "w-decolonization", "w-post-70s", "w-tech-era", "w-contemporary"],
    "w-cold-war": ["w-cold-war", "w-contemporary"],
    "w-decolonization": ["w-decolonization", "w-cold-war", "w-contemporary"],
    "w-post-70s": ["w-post-70s", "w-tech-era", "w-contemporary"],
    "w-tech-era": ["w-tech-era", "w-post-70s", "w-cold-war"],
    "w-east-asia": ["w-japan", "w-korea", "w-east-asia"],
    "w-japan": ["w-japan", "w-east-asia", "w-early-modern", "w-modern"],
    "w-korea": ["w-korea", "w-east-asia", "w-early-modern", "w-modern"],
    "w-southeast-asia": ["w-southeast-asia", "w-early-modern", "w-ming-qing", "w-age-of-sail"],
    "w-oceania": ["w-oceania", "w-early-modern", "w-age-of-sail", "w-imperialism"],
    "w-shan": ["w-shang", "w-ancient-china"],
    "w-shang": ["w-shang", "w-ancient-china", "w-zhou"],
    "w-zhou": ["w-zhou", "w-spring-autumn", "w-ancient-china"],
    "w-spring-autumn": ["w-spring-autumn", "w-zhou", "w-ancient-china"],
    "w-ancient-china": ["w-shang", "w-zhou", "w-spring-autumn", "w-cn-han", "w-cn-tang", "w-han-tang", "w-ancient-china"],
}


def best(y, ye, cur):
    cands = PREF.get(cur, [cur])
    # 1) 优先：起始年与结束年都在区间内的候选中，取跨度最小的（最具体）
    fits = []
    for c in cands:
        if c not in PM:
            continue
        p = PM[c]
        if p["startYear"] <= y <= p["endYear"] and (ye is None or (p["startYear"] <= ye <= p["endYear"])):
            fits.append((p["endYear"] - p["startYear"], c))
    if fits:
        return min(fits)[1]
    # 2) 次选：起始年在区间内的候选中，取跨度最小的
    fits = []
    for c in cands:
        if c not in PM:
            continue
        p = PM[c]
        if p["startYear"] <= y <= p["endYear"]:
            fits.append((p["endYear"] - p["startYear"], c))
    if fits:
        return min(fits)[1]
    # 3) 兜底：在全表里找包含起始年的最窄时期
    fits = []
    for c in IDS:
        p = PM[c]
        if p["startYear"] <= y <= p["endYear"]:
            fits.append((p["endYear"] - p["startYear"], c))
    if fits:
        return min(fits)[1]
    return cur


def main(path):
    raw = json.load(open(path, encoding="utf-8"))
    changed = 0
    for it in raw:
        if "role" in it or "ro" in it:
            continue
        y = it.get("y", it.get("year"))
        ye = it.get("ye", it.get("yearEnd"))
        cur = it.get("p") or it.get("periodId")
        nb = best(y, ye, cur)
        if nb != cur:
            changed += 1
            print(f"  {it['id']}: {cur} -> {nb}  (y={y}, ye={ye})")
            it["p"] = nb
        # 若 yearEnd 超出新时期区间，截断到区间内
        p = PM[nb]
        if ye is not None and not (p["startYear"] <= ye <= p["endYear"]):
            newye = min(max(ye, p["startYear"]), p["endYear"])
            if newye < y:
                newye = y
            it["ye"] = newye
            print(f"  {it['id']}: yearEnd {ye} -> {newye}")
            dt = it.get("dt") or it.get("dateText") or ""
            if "－" in dt:
                head = dt.split("－")[0]
                pre = "公元前" if y < 0 else "公元"
                it["dt"] = head + "－" + pre + str(newye) + "年"
    json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{path}: 调整 {changed} 条")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
