# -*- coding: utf-8 -*-
"""v2.4.0 批次3：修正中国近现代人物的时期归属。

发现：`cn-qing-late`（清后期，1820-1912）下堆了 33 人，其中大量是
**活跃于民国与中华人民共和国时期**的人物，被错误归到"清后期"：

  毛泽东(1893-1976)、周恩来(1898-1976)、刘少奇(1898-1969)、
  邓小平(1904-1997)、朱德(1886-1976)、彭德怀(1898-1974)、
  林彪(1907-1971)、陈云(1905-1995)、刘伯承(1892-1986)、
  董必武(1886-1975)、宋教仁(1882-1913)、黄兴(1874-1916)、
  张学良(1901-2001)、李宗仁(1891-1969)、胡适(1891-1962)…

后果：
  1) 「清后期」时期的人物列表严重失真——用户会看到毛泽东出现在晚清
  2) 「中华人民共和国」「近代」时期的代表人物几乎为空

修复策略：按人物的**主要政治活动时期**而非出生年归位。

  cn-modern-republic   (1912-1931)  民国初年：宋教仁、黄兴、蔡锷、段祺瑞…
  cn-modern-anti-japan (1931-1945)  抗日战争
  cn-modern-liberation (1945-1949)  解放战争
  cn-prc-early         (1949-1978)  毛泽东、周恩来、朱德、刘少奇、彭德怀、刘伯承
  cn-prc-reform        (1978-2012)  邓小平、陈云
  cn-prc-new-era       (2012-2026)

保留在 cn-qing-late 的：李鸿章、张之洞、康有为、梁启超、严复、
谭嗣同、詹天佑、袁世凯（清末人物）。

★ 中国史人物按 cn-* 的 periodId 字段归位，需同时写入分片与 OVERRIDE。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 人物 id : 目标 periodId
FIXES = {
    # ---- 中华人民共和国：开国与建设时期（1949-1978）----
    "fig-mao-zedong": "cn-prc-early",
    "fig-zhou-enlai": "cn-prc-early",
    "fig-zzbq2-zhude": "cn-prc-early",
    "fig-liu-shaoqi": "cn-prc-early",
    "fig-peng-dehuai": "cn-prc-early",
    "fig-liu-bocheng": "cn-prc-early",
    "fig-zzbq3-chenyun": "cn-prc-early",
    "fig-zzbq3-he-long": "cn-prc-early",
    "fig-zzbq3-ye-ting": "cn-prc-early",
    # ---- 改革开放时期（1978-2012）----
    "fig-deng-xiaoping": "cn-prc-reform",
    # ---- 民国初年（1912-1931）----
    "fig-song-jiaoren": "cn-modern-republic",
    "fig-huang-xing": "cn-modern-republic",
    "fig-cai-e": "cn-modern-republic",
    "fig-duan-qirui": "cn-modern-republic",
    "fig-zhang-xueliang": "cn-modern-anti-japan",
    "fig-li-zongren": "cn-modern-anti-japan",
    "fig-hu-shi": "cn-modern-republic",
    "fig-cai-yuanpei": "cn-modern-republic",
    "fig-zhang-taiyan": "cn-modern-republic",
    "fig-zhou-shuren": "cn-modern-republic",
}


def main():
    dry = "--dry-run" in sys.argv

    world = json.load(io.open(os.path.join(ROOT, "data", "china.json"), encoding="utf-8"))
    by_id = {f["id"]: f for f in world["figures"]}
    pm = {p["id"]: p for p in world["periods"]}

    resolved = {}
    for fid, target in FIXES.items():
        f = by_id.get(fid)
        if not f:
            continue
        cur = f.get("periodId")
        if cur == target:
            continue
        if target not in pm:
            print(f"  ! 目标时期不存在: {target}")
            continue
        print(f"  {f['name']:12s} {f.get('birthYear')}~{f.get('deathYear')}  {cur:18s} → {target}")
        resolved[fid] = target

    if not resolved:
        print("无需改动。")
        return

    # 补丁中国史分片（figdata_*.json / china_*.json 等）
    patterns = ["figdata_*.json", "china_*.json", "evdata_*.json", "_b*.json", "*_mine.json"]
    shards = []
    for pat in patterns:
        shards.extend(glob.glob(os.path.join(HERE, pat)))
    shards = sorted(set(shards))

    patched = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (
            (obj.get("figures") or []) + (obj.get("events") or []))
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            fid = rec.get("id")
            if fid in resolved:
                key = "p" if ("p" in rec and "periodId" not in rec) else "periodId"
                if rec.get(key) != resolved[fid]:
                    rec[key] = resolved[fid]
                    patched += 1
                    changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"\n补丁 {patched} 处。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("请运行 python tools/build_data.py 复核。")


if __name__ == "__main__":
    main()
