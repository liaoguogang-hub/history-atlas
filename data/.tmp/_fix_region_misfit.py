# -*- coding: utf-8 -*-
"""v2.4.0 批次1：修复地区专题时期的人物错挂（第二批）。

上一轮修掉了归期算法兜底造成的错挂，但审计发现**源数据里还有错挂**：

  w-old-world（古代非洲）      → 姜子牙（中国周朝政治家）
  w-korea（朝鲜）              → 冒顿单于（匈奴单于）
  w-near-east-persian（近东波斯）→ 索福克勒斯、伯里克利、希罗多德（希腊人）
  w-modern-south-asia（近代南亚）→ 维多利亚（英国女王）

这些都是 periodId 被错误标注，需修正到正确时期。

做法：
  1) 修正这些人物在源分片中的 periodId
  2) 同时在 reassign_figures.py 的 PERIOD_OVERRIDE 中登记，防止被算法再挪回去

注意：姜子牙、冒顿单于属于中国史人物，在世界史中应归入
「w-ancient-china」或其子时期；索福克勒斯等归「w-classical-greece」。
"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 人物 id : (新 periodId, 说明)
FIXES = {
    # 姜子牙：中国周朝开国功臣，世界史视角下归"古代中国"
    "fig-jiang-ziya": ("w-ancient-china", "周朝开国功臣"),
    # 冒顿单于：匈奴单于，与中国汉朝同时，归"古代中国"分支（世界史的中国线）
    "fig-modu-chanyu": ("w-ancient-china", "匈奴单于"),
    # 伯里克利、索福克勒斯、希罗多德：希腊人，归"古典希腊"
    "fig-pericles": ("w-classical-greece", "雅典政治家"),
    "fig-euripides-2": ("w-classical-greece", "索福克勒斯（id 命名有误）"),
    "fig-herodotus": ("w-classical-greece", "希腊历史学家"),
    # 维多利亚：英国女王，归"帝国主义时代"
    "fig-victoria": ("w-imperialism", "英国女王"),
}


def main():
    dry = "--dry-run" in sys.argv

    # 先确认这些 id 真实存在及其当前 periodId
    world = json.load(io.open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))
    by_id = {f["id"]: f for f in world["figures"]}

    resolved = {}
    for fid, (target, why) in FIXES.items():
        f = by_id.get(fid)
        if not f:
            print(f"  ! {fid} 不存在，跳过（{why}）")
            continue
        cur = f.get("periodId")
        print(f"  {f['name']:16s} {cur:24s} → {target:24s}  ({why})")
        resolved[fid] = target

    if not resolved:
        print("无可修正项。")
        return

    # 补丁源分片
    shards = sorted(glob.glob(os.path.join(HERE, "world_fig_*.json")))
    patched = 0
    for path in shards:
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        recs = obj if isinstance(obj, list) else (obj.get("figures") or [])
        changed = False
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            fid = rec.get("id")
            if fid in resolved and rec.get("periodId") != resolved[fid]:
                rec["periodId"] = resolved[fid]
                patched += 1
                changed = True
        if changed and not dry:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)

    print(f"\n补丁 {patched} 处分片内的 periodId。")
    if dry:
        print("[dry-run] 未写入。")
    else:
        print("\n下一步：把这些 id 加入 tools/reassign_figures.py 的 PERIOD_OVERRIDE，")
        print("      否则按生卒年归位会把它们再挪走。")


if __name__ == "__main__":
    main()
