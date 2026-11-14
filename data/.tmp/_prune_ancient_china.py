# -*- coding: utf-8 -*-
"""v2.0.0 批次3：精简 w-ancient-china 中的纯中国史复述。

背景：世界史 w-ancient-china（古代中国）下有 59 个事件，但其中大部分是
中国史 scope 已有内容的复述（商汤灭夏、牧野之战、安史之乱等），
世界史视角下价值有限；少数条目带跨文明对照价值
（如「汉与罗马两大帝国的同时期制度比较」「造纸术的西传与中亚造纸」）。

决策（用户确认）：**大幅精简，只留对照型**。
保留判据：事件名含跨文明/对照关键词。
排除误伤：名称含「亚述」「罗塞塔」「埃及」「贵弥」等非中国主题的条目要先排除，
        它们只是恰好挂在 w-ancient-china 下（本身是数据归属问题，本批不动）。

做法：改 data/world.json 对应的源分片（world_events_*.json），删除被精简事件，
      并清理所有指向它们的引用。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WORLD = os.path.join(ROOT, "data", "world.json")

# 跨文明/对照关键词（命中则保留）
COMPARE_KEYS = [
    "罗马", "贵霜", "波斯", "阿拉伯", "日本", "朝鲜", "印度", "欧洲",
    "同时", "同期", "比较", "对照", "中亚", "丝路", "贸易", "交流",
    "传播", "世界", "全球", "帝国", "西传", "东传", "秩序", "网络",
    # 宗教/技术/思想的跨文明传播，虽表象是「中国事件」，但世界史视角下有意义
    "佛教传入", "西行", "取经", "译经", "造纸术", "怛罗斯",
    "遣唐使", "大化改新", "锁国", "白银",
]

# 非中国主题（本身归属有误，但不在本批处理范围，一律保留不动）
NON_CHINA = ["亚述", "罗塞塔", "埃及", "赫梯", "巴比伦", "波斯波利斯"]


def iter_records(obj):
    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                yield it
    elif isinstance(obj, dict):
        for key in ("events", "figures", "periods"):
            for it in obj.get(key) or []:
                if isinstance(it, dict):
                    yield it


def main():
    dry = "--dry-run" in sys.argv
    world = json.load(io.open(WORLD, encoding="utf-8"))

    # 求 w-ancient-china 的子时期集合
    byp = {}
    for p in world["periods"]:
        byp.setdefault(p.get("parentId"), []).append(p["id"])

    def sub(pid):
        out = [pid]
        for x in byp.get(pid, []):
            out += sub(x)
        return out

    ids = set(sub("w-ancient-china"))
    events = [e for e in world["events"] if e.get("periodId") in ids]

    keep, drop = [], []
    for e in events:
        name = e.get("name") or ""
        if any(k in name for k in NON_CHINA):
            keep.append((e, "非中国主题，保留"))
        elif any(k in name for k in COMPARE_KEYS):
            keep.append((e, "含对照关键词"))
        else:
            drop.append(e)

    print(f"w-ancient-china 共 {len(events)} 条")
    print(f"  保留 {len(keep)} 条")
    print(f"  精简 {len(drop)} 条\n")

    print("=== 将删除 ===")
    for e in drop:
        print(f"  {e.get('year')}  {e['name']}")
    print("\n=== 保留 ===")
    for e, why in keep:
        print(f"  {e.get('year')}  {e['name']}  [{why}]")

    if dry:
        print("\n[dry-run] 未写入。")
        return

    drop_ids = {e["id"] for e in drop}

    # 补丁源分片
    shards = sorted(glob.glob(os.path.join(HERE, "world_events_*.json")))
    removed = 0
    refs = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        changed = False
        if isinstance(obj, list):
            for it in obj:
                if not isinstance(it, dict):
                    continue
                # 清理引用
                for key in ("figures", "relatedEvents", "relatedFigures",
                            "keyFigures", "f", "rf", "kf", "re"):
                    lst = it.get(key)
                    if isinstance(lst, list):
                        kept = [v for v in lst if v not in drop_ids]
                        if len(kept) != len(lst):
                            it[key] = kept
                            refs += len(lst) - len(kept)
                            changed = True
            # 删除事件本身
            before = len(obj)
            obj = [x for x in obj
                   if not (isinstance(x, dict) and x.get("id") in drop_ids)]
            if len(obj) != before:
                removed += before - len(obj)
                changed = True

        if changed:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)
            print(f"\n已更新 {os.path.basename(path)}")

    print(f"\n删除事件 {removed} 条，清理引用 {refs} 处。")

    # 自检
    for path in shards:
        try:
            txt = io.open(path, encoding="utf-8").read()
        except Exception:                              # noqa: BLE001
            continue
        for did in drop_ids:
            if f'"{did}"' in txt:
                raise SystemExit(f"自检失败：{os.path.basename(path)} 仍残留 {did}")
    print("自检通过：被删事件已无残留。")
    print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
