"""修正个别明显错误的人物时期归属。

背景：人物时期由 ``reassign_figures.py`` 按生卒年自动归位，
但少数条目在原始分片里就带了错误的 periodId，且因为生卒年缺失或
落在两个时期的重叠区，自动归位没能纠正它们。

本脚本只处理**已经人工确认**的条目，不做泛化推断——
史实上「西汉」与「东汉」的分界在王莽篡汉前后，
自动归位对跨越该节点的君主总会有偏差，逐一核对更可靠。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# id → (时期 id, 理由)
PERIOD_FIX = {
    # 汉高祖刘邦，前256—前195年在位，属西汉而非战国
    "fig-liu-bang": ("cn-han-west", "汉高祖刘邦，在位期间西汉开国"),
    # 东汉光武帝刘秀，生于战国末但事功全在东汉
    "fig-liu-xiu": ("cn-han-east", "东汉开国皇帝，事功全在新朝之后"),
}


def main():
    for path in sys.argv[1:]:
        d = json.load(io.open(path, encoding="utf-8"))
        changed = 0
        for f in d.get("figures") or []:
            spec = PERIOD_FIX.get(f.get("id"))
            if not spec:
                continue
            target, reason = spec
            if f.get("periodId") == target:
                continue
            old = f.get("periodId")
            f["periodId"] = target
            changed += 1
            print(f"   {f.get('name')}：{old} → {target}（{reason}）")
        if changed:
            io.open(path, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=1))
        print(f"{path}: 修正 {changed} 条时期归属")


if __name__ == "__main__":
    main()
