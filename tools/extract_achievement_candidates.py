"""为已有生平但缺成就列表的人物生成**候选**成就条目。

说明：这不是自动定稿。脚本只从生平里挑出「像成就」的句子作为候选，
供人工挑选与改写。直接拿去当最终数据风险太高——生平里的句子往往
是叙述而非概括，摘出来读着别扭。

挑选规则（尽量保守，宁少勿滥）：
1. 句子里含朝代年份（如「元朔六年」「公元前104年」）或明确的
   功业动词（统一、灭、破、封、筑、创、颁、行、著、联姻……）。
2. 句子长度在 10-60 字之间，太长的读着累，太短没信息。
3. 去掉「他/其/此人」开头的句子（第三人称转述不适合当成就条目）。
4. 每条候选去掉句末句号，作为条目文本。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

YEAR = re.compile(r"(公元前)?[前]?\d{1,4}年|元年|初年|年间|末年|即位|登基|称帝|建国|称王")
ACTION = re.compile(
    r"统一|灭[了国]|灭[下]|破[了敌]|大破|击败|平定|定鼎|建立|创立|首创|颁[发布]|推行|实行|改革|"
    r"建[立都]|定都|迁都|设[立置]|开创|兴[办起]|修[建筑]|著[作]|撰写|编[纂撰]|完成|提出|"
    r"拓展|开辟|开[疆土]|开发|治理|经略|征服|受封|封为|封[一个子爵位号]|联姻|和亲|会盟|"
    r"登基|即位|称[王帝]|摄政|辅政|摄政|掌[权政]|专权|起兵|举兵|会战|战役|远航|下西洋")

STOP_START = re.compile(r"^(他|其|此人|是|这|那|后来|此后|同时|另外|此外|于是|从此|当时|以及|并且)")


def sentences(text):
    """按中文句读切句，保留标点信息。"""
    parts = re.split(r"(?<=[。；！？])", text)
    return [p.strip() for p in parts if p.strip()]


def candidates(bio):
    out = []
    for s in sentences(bio):
        s2 = s.rstrip("。；！？")
        if not (10 <= len(s2) <= 60):
            continue
        if STOP_START.match(s2):
            continue
        score = 0
        if YEAR.search(s2):
            score += 2
        if ACTION.search(s2):
            score += 2
        if score >= 2:
            out.append((score, s2))
    # 分数高的排前面
    out.sort(key=lambda x: -x[0])
    return [s for _, s in out]


def main():
    path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    d = json.load(io.open(path, encoding="utf-8"))
    periods = {p["id"]: p.get("name") for p in d["periods"]}

    rows = []
    for f in d["figures"]:
        if f.get("achievements"):
            continue
        bio = f.get("biography") or ""
        if len(bio) < 200:
            continue
        cands = candidates(bio)
        if not cands:
            continue
        rows.append({
            "id": f["id"],
            "name": f.get("name"),
            "period": periods.get(f.get("periodId")),
            "candidates": cands[:8],
        })

    print(f"=== {path} ===")
    print(f"可从生平提取候选的人物: {len(rows)} 人")
    for r in rows[:12]:
        print(f"\n-- {r['id']} {r['name']}（{r['period']}）--")
        for c in r["candidates"][:5]:
            print(f"   · {c}")

    if out_path:
        io.open(out_path, "w", encoding="utf-8").write(
            json.dumps(rows, ensure_ascii=False, indent=1))
        print(f"\n候选已写入 {out_path}")


if __name__ == "__main__":
    main()
