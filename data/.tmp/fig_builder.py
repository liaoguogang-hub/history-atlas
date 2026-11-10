# -*- coding: utf-8 -*-
"""人物构建：紧凑元组 -> SCHEMA §4 记录。"""

def build(raw):
    out = []
    for r in raw:
        fid, name, alias, birth, death, role, pid, gender, summary, bio, ach, quotes, rev, rfig, tags = r
        if birth is not None and death is not None:
            b = "公元前%d年" % abs(birth) if birth < 0 else "公元%d年" % birth
            d = "公元前%d年" % abs(death) if death < 0 else "公元%d年" % death
            life = b + "－" + d
        elif birth is not None:
            b = "公元前%d年" % abs(birth) if birth < 0 else "公元%d年" % birth
            life = b + "－？"
        elif death is not None:
            d = "公元前%d年" % abs(death) if death < 0 else "公元%d年" % death
            life = "？－" + d
        else:
            life = "不详"
        out.append({
            "id": fid,
            "name": name,
            "alias": alias,
            "birthYear": birth,
            "deathYear": death,
            "lifeText": life,
            "role": role,
            "periodId": pid,
            "gender": gender,
            "summary": summary,
            "biography": bio,
            "achievements": list(ach),
            "quotes": list(quotes),
            "relatedEvents": list(rev),
            "relatedFigures": list(rfig),
            "tags": list(tags),
        })
    return out
