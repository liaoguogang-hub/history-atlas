"""清理「被引用但事实上不存在」的人物占位条目。

背景：原始分片里，部分时期与事件引用了并不存在于 figures 中的 id
（如 cn-nanbei-south 的 keyFigures 引用了 fig-xiao-yan）。早期为了让
校验通过，auto_fill_dangling 会为这些 id 造一条空壳人物，名字还是由
拼音音译出来的（「Zhang·Jia」「Zhao·Sulfou·Gong」）。这些条目没有
考据依据，放进人物志反而有害。

本步骤做两件事：
1. 删除所有「传记仍为占位文本」且「名字含拉丁字母」的图省事条目
2. 把它们在 periods / events / figures 中的引用一并剔除

宁可时期卡片少一个人物链接，也不保留一条来历不明的人物。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

LATIN = re.compile(r"[A-Za-z]")
PLACEHOLDER_MARKS = ("待补充条目",)


def is_fabricated(f):
    """是否为无考据依据的自动生成条目。"""
    bio = f.get("biography") or ""
    if not any(m in bio for m in PLACEHOLDER_MARKS):
        return False
    name = f.get("name") or ""
    # 名字里带拉丁字母或间隔号，说明是音译产物，不是可靠人名
    return bool(LATIN.search(name)) or "·" in name


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        figs = d.get("figures") or []

        # 只删除「音译名 + 占位传记」的组合；
        # 名字已是纯中文的占位条目保留，它们至少有可靠的人名。
        drop = {f["id"] for f in figs if is_fabricated(f)}
        if not drop:
            print(f"{path}: 无需清理")
            continue

        d["figures"] = [f for f in figs if f["id"] not in drop]

        pruned_refs = 0
        for kind in ("periods", "events", "figures"):
            for item in d.get(kind) or []:
                for field in ("keyFigures", "figures", "relatedFigures"):
                    vals = item.get(field)
                    if not vals:
                        continue
                    kept = [v for v in vals if v not in drop]
                    if len(kept) != len(vals):
                        pruned_refs += len(vals) - len(kept)
                        if kept:
                            item[field] = kept
                        else:
                            item.pop(field, None)

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: 删除 {len(drop)} 条无考据占位人物，"
              f"剔除 {pruned_refs} 处引用，人物 {len(figs)} -> {len(d['figures'])}")


if __name__ == "__main__":
    main()
