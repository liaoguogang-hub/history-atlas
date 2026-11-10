import io
import json
import os
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

china = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))

cn_figs = {f["id"]: f for f in china["figures"]}
w_by_id = {f["id"]: f for f in world["figures"]}

# 世界史中，与中国史同 id 但内容是空壳占位的人物 → 用中国史的真实数据覆盖
# 覆盖时：periodId 改为世界史对应时期，其余字段保留中国史的真实内容。
#
# 中国史时期 → 世界史时期
w_period_ids = {p["id"] for p in world["periods"]}
w_period_by_id = {p["id"]: p for p in world["periods"]}

# 中国史时期 → 世界史时期。
# 优先用显式映射；未列出的按语义关键词匹配世界史时期；
# 都匹配不上时退回「古代中国」。
CN_TO_W = {
    "cn-prehistory": "w-prehistory",
    "cn-xia-shang": "w-ancient-china",
    "cn-zhou-west": "w-ancient-china",
    "cn-zhou-east": "w-ancient-china",
    "cn-spring-autumn": "w-spring-autumn",
    "cn-warring-states": "w-ancient-china",
    "cn-qin": "w-ancient-china",
    "cn-han": "w-han-tang",
    "cn-han-west": "w-han-tang",
    "cn-han-east": "w-han-tang",
    "cn-three-kingdoms": "w-han-tang",
    "cn-three-shu": "w-han-tang",
    "cn-three-wei": "w-han-tang",
    "cn-three-wu": "w-han-tang",
    "cn-liang-jin": "w-medieval-china",
    "cn-jin-west": "w-medieval-china",
    "cn-jin-east": "w-medieval-china",
    "cn-sixteen-kingdoms": "w-medieval-china",
    "cn-nanbei": "w-medieval-china",
    "cn-nanbei-north": "w-medieval-china",
    "cn-nanbei-south": "w-medieval-china",
    "cn-sui": "w-han-tang",
    "cn-sui-tang": "w-han-tang",
    "cn-tang": "w-han-tang",
    "cn-tang-early": "w-han-tang",
    "cn-tang-mid": "w-han-tang",
    "cn-tang-late": "w-han-tang",
    "cn-wudai": "w-tang-song",
    "cn-wudai-north": "w-tang-song",
    "cn-wudai-south": "w-tang-song",
    "cn-song-liao-jin": "w-tang-song",
    "cn-song": "w-tang-song",
    "cn-song-north": "w-tang-song",
    "cn-song-south": "w-tang-song",
    "cn-liao": "w-tang-song",
    "cn-jin": "w-tang-song",
    "cn-xixia": "w-tang-song",
    "cn-yuan": "w-ming-qing",
    "cn-yuan-early": "w-ming-qing",
    "cn-yuan-late": "w-ming-qing",
    "cn-ming": "w-ming-qing",
    "cn-ming-early": "w-ming-qing",
    "cn-ming-mid": "w-ming-qing",
    "cn-ming-late": "w-ming-qing",
    "cn-qing": "w-ming-qing",
    "cn-qing-early": "w-ming-qing",
    "cn-qing-mid": "w-ming-qing",
    "cn-qing-late": "w-ming-qing",
    "cn-modern": "w-modern",
    "cn-modern-republic": "w-modern",
    "cn-modern-anti-japan": "w-world-wars",
    "cn-modern-liberation": "w-cold-war",
    "cn-prc": "w-post-70s",
    "cn-prc-early": "w-cold-war",
    "cn-prc-reform": "w-post-70s",
    "cn-prc-new-era": "w-post-70s",
    "cn-mongol": "w-mongol-empire",
    "cn-wangmang": "w-han-tang",
}

# 中国史时期名 → 世界史时期名的关键词匹配（用于未显式列出的时期）
CN_KEYWORDS = [
    (("春秋", "战国", "先秦", "夏", "商", "周"), "w-ancient-china"),
    (("秦",), "w-ancient-china"),
    (("汉", "三国", "晋", "隋", "唐"), "w-han-tang"),
    (("南北朝", "十六国", "魏", "蜀", "吴"), "w-medieval-china"),
    (("五代", "十国", "宋", "辽", "金", "西夏"), "w-tang-song"),
    (("元", "明", "清"), "w-ming-qing"),
    (("蒙古",), "w-mongol-empire"),
    (("民国", "近代"), "w-modern"),
    (("抗日", "解放"), "w-world-wars"),
    (("中华人民共和国", "社会主义", "改革", "新时代"), "w-post-70s"),
    (("史前",), "w-prehistory"),
]


def map_period(cn_period_id, cn_period_name):
    """把中国史时期映射到世界史时期。"""
    if cn_period_id in CN_TO_W and CN_TO_W[cn_period_id] in w_period_ids:
        return CN_TO_W[cn_period_id]
    for keys, target in CN_KEYWORDS:
        if any(k in (cn_period_name or "") for k in keys):
            if target in w_period_ids:
                return target
    if "w-ancient-china" in w_period_ids:
        return "w-ancient-china"
    return next(iter(w_period_ids))


def is_placeholder(f):
    return "待补充条目" in (f.get("biography") or "")


def slug(fid):
    return re.sub(r"[^0-9a-zA-Z]+", "-", fid).strip("-").lower()


copied = 0
skipped = 0
# 中国史人物按规范化 id 建立索引，便于与世界史里的同 id 匹配
cn_index = {}
for fid, cf in cn_figs.items():
    cn_index.setdefault(slug(fid), cf)

cn_period_name = {p["id"]: p.get("name") or "" for p in china["periods"]}

for fid, wf in list(w_by_id.items()):
    cf = cn_index.get(slug(fid))
    if not cf:
        continue
    if not is_placeholder(wf):
        continue          # 世界史已有自己的真实内容，不覆盖
    target_period = map_period(cf.get("periodId"),
                               cn_period_name.get(cf.get("periodId")))
    new_f = dict(cf)
    new_f["id"] = fid
    new_f["periodId"] = target_period
    # 关系引用只保留世界史中确实存在的人/事件
    new_f["relatedFigures"] = [
        r for r in (cf.get("relatedFigures") or [])
        if r in w_by_id and r != fid
    ]
    new_f["relatedEvents"] = [
        r for r in (cf.get("relatedEvents") or [])
        if any(e["id"] == r for e in world["events"])
    ]
    w_by_id[fid] = new_f
    copied += 1

world["figures"] = list(w_by_id.values())

io.open(os.path.join(ROOT, "data", "world.json"), "w", encoding="utf-8").write(
    json.dumps(world, ensure_ascii=False, indent=1))
print(f"world.json: copied {copied} real china figures, skipped {skipped}")
