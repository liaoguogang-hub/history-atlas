import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
data = json.load(io.open(path, encoding="utf-8"))
periods = data["periods"]
period_ids = {p["id"] for p in periods}

# 中国史时期树缺少的分支：西夏、蒙古帝国（元的前身）、金（已有）、
# 三国归晋的过渡等。补齐后人物/事件的 periodId 才有着落。
NEW = [
    {
        "id": "cn-xixia",
        "name": "西夏",
        "startYear": 1038,
        "endYear": 1227,
        "parentId": "cn-song-liao-jin",
        "colorKey": "green",
        "summary": "党项李氏建立的政权，与宋、辽、金鼎立1038年，创制西夏文并信仰佛教，1227年蒙古灭之。",
        "tags": ["西夏", "党项", "唐宋时期"],
    },
    {
        "id": "cn-mongol",
        "name": "蒙古帝国",
        "startYear": 1206,
        "endYear": 1271,
        "parentId": "cn-yuan",
        "colorKey": "yuan",
        "summary": "成吉思汗1206年建立大蒙古国，统一草原诸部，创立八旗式的十进制军制与驿站体系，并西征花剌子模，兵锋直抵东欧。",
        "tags": ["蒙古", "成吉思汗", "元朝前身"],
    },
]

added = []
for np in NEW:
    if np["id"] in period_ids:
        continue
    # 只有当父时期存在时才新增，避免造出孤立节点
    parent = np.get("parentId")
    if parent and parent not in period_ids:
        continue
    periods.append(np)
    period_ids.add(np["id"])
    added.append(np["id"])

# 修正指向不存在时期的 periodId：
#   优先用 FALLBACK 显式映射；否则用「同一 id 在本数据中已存在的同类时期」兜底。
FALLBACK = {
    "cn-xixia": "cn-song-liao-jin",
    "w-mongol-empire": "cn-mongol",
    "cn-song": "cn-song-liao-jin",
    # 世界史常见笔误 → 正确时期
    "w-ancient-india": "w-ancient-south-asia",
    "w-mediterral-islam": "w-medieval-islam",
    "w-islamic-golden-2": "w-islamic-golden",
    "w-classical-greece-2": "w-classical-greece",
    "w-roman-2": "w-roman",
    "w-early-modern-2": "w-early-modern",
}
fixed = []
for kind in ("figures", "events"):
    for item in data.get(kind) or []:
        pid = item.get("periodId")
        if pid and pid not in period_ids:
            new_pid = FALLBACK.get(pid)
            if new_pid and new_pid in period_ids:
                item["periodId"] = new_pid
                fixed.append((item["id"], pid, new_pid))
            else:
                # 兜底：同 scope 内找最接近的时期（按尾段相似度）
                tail = pid.split("-")[-1]
                cand = [p for p in period_ids if p.split("-")[-1] == tail]
                if len(cand) == 1:
                    item["periodId"] = cand[0]
                    fixed.append((item["id"], pid, cand[0]))

io.open(path, "w", encoding="utf-8").write(
    json.dumps(data, ensure_ascii=False, indent=1))
print(f"{path}: +{len(added)} periods ({', '.join(added)}), fixed {len(fixed)} periodIds")
for f in fixed[:10]:
    print("   ", f)
