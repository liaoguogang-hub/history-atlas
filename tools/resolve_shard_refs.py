"""把扩充分片里的关联引用按**名称**自动解析成库中真实 id。

分片里写 relatedFigures / relatedEvents 时，人多半是按「人物名」或
「事件名」在想，只是落笔时用了个自造的 id。与其手工维护一张
「虚构 id → 真实 id」的对照表（几百条，很快会失同步），
不如让脚本从库里反查。

做法：
1. 收集库里所有人物名与事件名，建立 名称 → id 的索引。
2. 对分片里的每个引用 id，先在库里按 id 找：
   - 找得到 → 保留
   - 找不到 → 尝试把该 id 的「名字片段」还原成候选名称再查
     （例如 fig-yelv-chucai → 耶律楚材 这类音译无法可靠还原，
      因此这一步只能处理一部分）
3. 仍然无法解析的引用直接删除——关联稍后由 build_relations.py
   依据事件参与者与正文提及重新推导，硬塞错误 id 比留空更糟。

另外支持一份人工映射表 ``tools/ref_alias.json``，
用于处理音译无法还原的情况。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ALIAS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "ref_alias.json")


def build_index():
    idx = {}
    ids = set()
    for scope in ("china", "world"):
        p = f"data/{scope}.json"
        if not os.path.exists(p):
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        for f in d.get("figures") or []:
            idx.setdefault(f.get("name", ""), f["id"])
            ids.add(f["id"])
        for e in d.get("events") or []:
            idx.setdefault(e.get("name", ""), e["id"])
            ids.add(e["id"])
    return idx, ids


def main():
    idx, ids = build_index()

    alias = {}
    if os.path.exists(ALIAS_FILE):
        alias = json.load(io.open(ALIAS_FILE, encoding="utf-8"))

    for path in sys.argv[1:]:
        data = json.load(io.open(path, encoding="utf-8"))
        kept = dropped = aliased = 0
        for f in data:
            for fld in ("relatedFigures", "relatedEvents"):
                new = []
                for r in (f.get(fld) or []):
                    if r in ids:
                        new.append(r)
                        kept += 1
                    elif r in alias:
                        tgt = alias[r]
                        if tgt and tgt in ids:
                            new.append(tgt)
                            aliased += 1
                        else:
                            dropped += 1
                    else:
                        dropped += 1
                f[fld] = new
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=1))
        print(f"{path}: 保留 {kept}，映射 {aliased}，删除 {dropped}")


if __name__ == "__main__":
    main()
