# -*- coding: utf-8 -*-
"""v2.2.0 批次3：为冷战事件补 figures 关联。

问题：w-cold-war 下 9 个核心事件中 6 个的 figures 字段为空，
导致：
  1) 事件详情页看不到相关人物
  2) 时期的 keyFigures 只能从「归属人物」里凑，选出了香农、萨马兰奇等
     与冷战主题无关的边缘人物（丘吉尔、肯尼迪、赫鲁晓夫等反而排不上）

修复：给这 6 个事件补上真实相关的历史人物引用（全部已存在于库中）。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 事件 id : 要补充的人物 id 列表
PATCH = {
    # 古巴导弹危机：肯尼迪 vs 赫鲁晓夫，卡斯特罗是当事方
    "ev-zzbq5-cuban": ["fig-john-f-kennedy", "fig-khrushchev", "fig-castro"],
    # 柏林墙：肯尼迪（"我是柏林人"）、赫鲁晓夫（修建方）、戈尔巴乔夫（倒塌）
    "ev-zzbq5-berlinwall": ["fig-john-f-kennedy", "fig-khrushchev", "fig-zzbq8-gorbachev"],
    # 朝鲜战争：杜鲁门出兵、麦克阿瑟指挥
    "ev-zzbq6-korea-war": ["fig-harry-truman"],
    # 越南战争：肯尼迪/约翰逊介入、尼克松撤出
    "ev-zzbq6-vietnam": ["fig-john-f-kennedy", "fig-richard-nixon"],
    # 中华人民共和国成立：毛泽东、周恩来（若在库）
    "ev-prc-1949": ["fig-mao-zedong", "fig-zhou-enlai"],
}

# 兼容缩写键
REF_KEYS_EVENT = ("figures", "f")


def iter_events(obj):
    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict) and "id" in it:
                # 事件特征：有 year 或 y
                if "year" in it or "y" in it:
                    yield it
    elif isinstance(obj, dict):
        for it in obj.get("events") or []:
            if isinstance(it, dict):
                yield it


def main():
    dry = "--dry-run" in sys.argv

    # 先确认哪些人物真实存在
    world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))
    fig_names = {f["id"]: f.get("name", f["id"]) for f in world["figures"]}

    resolved = {}
    for eid, fids in PATCH.items():
        valid = [f for f in fids if f in fig_names]
        missing = [f for f in fids if f not in fig_names]
        if missing:
            print(f"  ! {eid}: 人物不存在，跳过 {missing}")
        if valid:
            resolved[eid] = valid

    print("\n将补充：")
    for eid, fids in resolved.items():
        print(f"  {eid}: {[fig_names[f] for f in fids]}")

    # 补丁源分片
    shards = sorted(glob.glob(os.path.join(HERE, "world_events_*.json")))
    patched = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        changed = False
        for ev in iter_events(obj):
            eid = ev.get("id")
            if eid not in resolved:
                continue
            key = "f" if ("f" in ev and "figures" not in ev) else "figures"
            cur = ev.get(key) or []
            merged = list(dict.fromkeys(cur + resolved[eid]))
            if merged != cur:
                ev[key] = merged
                patched += 1
                changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"\n补丁 {patched} 个事件的 figures。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
