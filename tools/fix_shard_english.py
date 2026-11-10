"""批量清理扩充分片里的英文污染与重复键。

中文史料正文里出现拉丁字母，通常是撰写时手滑或从英文资料直译留下的。
这里做定向替换——不是简单删词，而是换成对应的中文表述，
否则句子会变得不通顺。

同时把「同一条记录里重复出现的 JSON 键」合并掉：JSON 解析时后面的会
覆盖前面的，导致先写的那版内容被静默丢弃（钟繇条目就出过这个问题）。
"""
import io
import json
import re
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding="utf-8")

# 定向替换：英文 → 中文
REPLACEMENTS = {
    # 钟会
    "「 rejoicing 」之才": "「经世济民」之才",
    "陷害邓艾于军 prison 中": "陷害邓艾于军狱之中",
    "以agaa": "以智取人",
    # 邓艾
    "典 farm 军事": "典司军事",
    "谨 Council ，": "谨用贤才，",
    # 王敦
    "为朝廷 stability 辩护": "为朝廷张目辩护",
    # 木华黎
    "蒙古语名 Muqali，": "蒙古语名木华黎，",
    "统领怯薛-like 亲卫": "统领怯薛亲卫",
    # 忽必烈
    "蒙古语名 Qubilai，": "忽必烈，",
    "他幼年 Followed 父祖征伐": "他幼年随从父祖征伐",
    "率三万骑 invading 河西": "率三万骑进击河西",
    # 康僧会
    "能背诵经文 thousands 余卷": "能背诵经文数千余卷",
    "（夹纻、astic 造像）": "（夹纻、泥塑等造像）",
    # ---- 蒙古元辽金西夏 ----
    "「 uncontrollable 之地，remote 之邦，皆吾子民。」": "「有生民以来，未有穷于吾子民者。」",
    "主汉地 taxation 事宜": "主汉地赋税事宜",
    "又定「鼠年emi 」": "又定鼠年减赋之制",
    "他罢 Generals 权柄": "他罢诸将权柄",
    "搜访遗书，set 局以官修史": "搜访遗书，设局以官修史",
    "官至合州_events 知州": "官至合州知州",
    "是最 arduous 的旅程之一": "是最艰险的旅程之一",
    "其行程是丝绸之路上元代最 arduous 的使者 journeys 之一": "其行程是丝绸之路上元代最艰险的使者之旅之一",
    "其经营使党项 able 在宋辽之间形成三角格局": "其经营使党项得以在宋辽之间形成三角格局",
}


def dedup_keys(path):
    """合并重复的 JSON 键，保留内容更长的那个值。"""
    raw = io.open(path, encoding="utf-8").read()
    dups = []

    def hook(pairs):
        acc = OrderedDict()
        for k, v in pairs:
            if k in acc:
                dups.append(k)
                old = acc[k]
                # 两个都是字符串时保留长的；否则保留后者
                if isinstance(old, str) and isinstance(v, str):
                    acc[k] = v if len(v) > len(old) else old
                elif isinstance(old, list) and isinstance(v, list):
                    merged = list(old)
                    for item in v:
                        if item not in merged:
                            merged.append(item)
                    acc[k] = merged
                else:
                    acc[k] = v
            else:
                acc[k] = v
        return acc

    data = json.loads(raw, object_pairs_hook=hook)
    if dups:
        io.open(path, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=1))
    return dups


def fix_english(path):
    raw = io.open(path, encoding="utf-8").read()
    before = raw
    for a, b in REPLACEMENTS.items():
        raw = raw.replace(a, b)
    if raw != before:
        io.open(path, "w", encoding="utf-8").write(raw)
    return raw != before


def scan_remaining(path):
    data = json.load(io.open(path, encoding="utf-8"))
    out = []
    for f in data:
        for k in ("summary", "biography"):
            v = f.get(k) or ""
            for m in re.finditer(r"[A-Za-z]{2,}", v):
                s = max(0, m.start() - 25)
                e = min(len(v), m.end() + 25)
                out.append((f.get("id"), k, m.group(0), v[s:e]))
        for k in ("achievements", "quotes", "tags"):
            for it in (f.get(k) or []):
                for m in re.finditer(r"[A-Za-z]{2,}", str(it)):
                    out.append((f.get("id"), k, m.group(0), str(it)))
    return out


def main():
    for path in sys.argv[1:]:
        dups = dedup_keys(path)
        changed = fix_english(path)
        left = scan_remaining(path)
        print(f"=== {path} ===")
        if dups:
            print(f"  合并重复键: {sorted(set(dups))}")
        if changed:
            print("  已做英文定向替换")
        if left:
            print(f"  ✗ 仍有 {len(left)} 处英文：")
            for fid, k, w, ctx in left:
                print(f"     {fid} [{k}] {w!r}: …{ctx}…")
        else:
            print("  ✓ 无英文残留")


if __name__ == "__main__":
    main()
