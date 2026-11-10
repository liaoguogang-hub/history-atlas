"""清理合并遗留的碎片化字段。

两件事：
1. achievements 里混进了合并时带过来的短碎片（如「据江东」「三分天下」），
   单独看没有信息量，与其它条目并列时还显得重复。
2. 名言归属错误：把「生子当如孙仲谋」记在孙权名下，
   这句其实是曹操赞叹孙权的话，应归到曹操。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

MIN_ACHIEVEMENT_LEN = 8

# 需要从某个条目移除、改挂到另一个人物名下的名言
MOVE_QUOTES = [
    ("fig-sunquan", "生子当如孙仲谋。", "fig-han-east-cao-cao",
     "生子当如孙仲谋。"),
]


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        figs = {f["id"]: f for f in d.get("figures") or []}

        # 1. 清理过短的成就碎片
        trimmed = 0
        for f in figs.values():
            ach = f.get("achievements") or []
            kept = [a for a in ach if len((a or "").strip()) >= MIN_ACHIEVEMENT_LEN]
            # 全部都很短时保留原样，避免把条目清空
            if kept and len(kept) != len(ach):
                f["achievements"] = kept
                trimmed += len(ach) - len(kept)

        # 2. 修正名言归属
        moved = 0
        for src_id, quote, dst_id, dst_quote in MOVE_QUOTES:
            src, dst = figs.get(src_id), figs.get(dst_id)
            if not src or not dst:
                continue
            q = src.get("quotes") or []
            if quote not in q:
                continue
            src["quotes"] = [x for x in q if x != quote]
            dq = dst.get("quotes") or []
            if dst_quote not in dq:
                dq.append(dst_quote)
            dst["quotes"] = dq
            moved += 1

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: 清理短成就 {trimmed} 条，修正名言归属 {moved} 处")


if __name__ == "__main__":
    main()
