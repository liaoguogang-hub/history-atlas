#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 eventId -> {period, y, ye, dt?} 精确修补事件。"""
import json, sys, os

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(D, "world_periods.json"), encoding="utf-8"))
PM = {p["id"]: p for p in P}


def fmt(year, suffix=""):
    pre = "公元前" if year < 0 else "公元"
    return f"{pre}{abs(year)}年{suffix}"


PATCH = {
 "ev-pre-lapita-navigation": {"p":"w-ancient-near-east","y":-3300,"ye":-800,"dt":"公元前3300年－公元前800年"},
 "ev-persia-cyrus-conquest": {"p":"w-near-east-persian","y":-546,"ye":-539,"dt":"公元前546年－公元前539年"},
 "ev-persia-zoroaster": {"p":"w-near-east-persian","y":-550,"ye":-330,"dt":"公元前550年－公元前330年"},
 "ev-persia-marathon": {"p":"w-archaic-greece","y":-490,"ye":-480,"dt":"公元前490年－公元前480年"},
 "ev-hellenistic-india-gandhara": {"p":"w-roman-empire","y":50,"ye":300,"dt":"公元50年－公元300年"},
 "ev-hellenistic-kushan": {"p":"w-roman-empire","y":78,"ye":180,"dt":"公元78年－公元180年"},
 "ev-rome-china-han-parallel": {"p":"w-cn-han","y":-202,"ye":220,"dt":"公元前202年－公元220年"},
 "ev-punic-war-maritime-commercial": {"p":"w-roman-republic","y":-300,"ye":-100,"dt":"公元前300年－公元前100年"},
 "ev-rome-egypt-alexandria-library": {"p":"w-roman-empire","y":-25,"ye":395,"dt":"公元前25年－公元395年"},
 "ev-rome-punic-mediterranean-anthology": {"p":"w-roman-republic","y":-312,"ye":-100,"dt":"公元前312年－公元前100年"},
 "ev-rome-mauryan-parthian": {"p":"w-roman-republic","y":-100,"ye":-27,"dt":"公元前100年－公元前27年"},
 "ev-rome-latin-church-latin-greek": {"p":"w-post-roman-europe","y":476,"ye":800,"dt":"公元476年－公元800年"},
 "ev-rome-egypt-ibis": {"p":"w-ancient-near-east","y":-650,"ye":-360,"dt":"公元前650年－公元前360年"},
 "ev-rome-arabesque-commercial": {"p":"w-roman-empire","y":-25,"ye":300,"dt":"公元前25年－公元300年"},
 "ev-rome-carthage-punic-god": {"p":"w-punic-war","y":-264,"ye":-146,"dt":"公元前264年－公元前146年"},
 "ev-rome-handicraft-bread": {"p":"w-roman-empire","y":-25,"ye":200,"dt":"公元前25年－公元200年"},
}


def main(path):
    raw = json.load(open(path, encoding="utf-8"))
    for it in raw:
        eid = it.get("id")
        if eid in PATCH:
            for k, v in PATCH[eid].items():
                it[k] = v
    json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{os.path.basename(path)}: 修补 {len(PATCH)} 条")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
