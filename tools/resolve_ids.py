"""在扩充分片里自动解析人物与事件名称 → 库中真实 id。

分片里写 relatedFigures 时常按「人物名」思考，但落笔时用了自己编的 id。
本脚本提供两类帮助：
1. ``resolve`` 子命令：给定名称，返回库中真实存在的 id（可含多个候选）。
2. ``fix`` 子命令：把分片里「名称 → id」的对照写进一个映射文件，
   供 fix_shard_refs.py 使用。

用法:
    python tools/resolve_ids.py find 王祯
    python tools/resolve_ids.py list 王祯 朱元璋
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def load():
    ids = {}
    for scope in ("china", "world"):
        d = json.load(io.open(f"data/{scope}.json", encoding="utf-8"))
        for f in d["figures"]:
            ids.setdefault(f.get("name", ""), []).append((scope, f["id"], f))
        for e in d["events"]:
            ids.setdefault(e.get("name", ""), []).append((scope, e["id"], e))
    return ids


def find(ids, name):
    if name in ids:
        return ids[name]
    # 包含匹配
    return [(sc, i, o) for k, v in ids.items() if name and name in k for sc, i, o in v]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    mode = sys.argv[1]
    ids = load()
    if mode == "find":
        for name in sys.argv[2:]:
            hits = find(ids, name)
            if not hits:
                print(f"{name}: 未找到")
            for sc, i, o in hits:
                kind = "人物" if "biography" in o else "事件"
                period = o.get("periodId", "")
                print(f"{name}: [{sc}] {kind} {i}  ({period})")
    elif mode == "list":
        # 列出所有含指定关键字的人物
        for name in sys.argv[2:]:
            print(f"--- 含「{name}」的人物 ---")
            for sc, i, o in ids.items():
                pass
            for k, v in ids.items():
                if name and name in k:
                    for sc, i, o in v:
                        if "biography" in o:
                            print(f"  {i:26s} {k}")


if __name__ == "__main__":
    main()
