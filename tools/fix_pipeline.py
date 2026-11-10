"""数据修复流水线：把一份 scope 数据修到 validate ERROR = 0。

用法:
    python tools/fix_pipeline.py data/china.json
    python tools/fix_pipeline.py data/world.json
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)


def run(script, *args):
    cmd = [sys.executable, os.path.join(TOOLS, script)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return (r.stdout or "") + (r.stderr or "")


def validate(path):
    out = run("validate_data.py", "--summary", path)
    m = re.search(r"-> 错误 (\d+) / 警告 (\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def main():
    path = sys.argv[1]
    scope = sys.argv[2] if len(sys.argv) > 2 else (
        "world" if "world" in os.path.basename(path) else "china")

    steps = [
        ("fix_year_order.py", path),
        ("fix_year_signs.py", path),
        ("fix_event_years.py", path),
        ("fix_year_order.py", path),
    ]
    if scope == "china":
        steps.append(("backfill_missing.py", path))
    steps += [
        ("auto_fill_dangling.py", path),
        # 修复被 slugify 压坏的 id，并合并同一个人物的重复条目
        ("fix_broken_ids.py", path),
        ("merge_duplicate_figures.py", path),
        # 删除音译推测出来、没有考据依据的占位人物及其引用
        ("prune_fabricated.py", path),
        ("fix_year_order.py", path),
        ("add_missing_periods.py", path),
        ("fix_year_order.py", path),
        # 校正时期树的史实结构（十国挂到五代十国下、宋辽金起始年等）
        ("fix_period_structure.py", path),
        # 先按 dateText 校正年份符号（否则下面按年份归位会用错年份），
        # 并校正战国、隋朝等时期边界
        ("fix_span_events.py", path),
        ("reassign_periods.py", path),
        # 归位后，跨度横跨多个子时期的事件上移到能容纳的父时期
        ("fix_span_events.py", path),
        # 跨文明专题事件集中挂到 w-cross-civilization（见该脚本注释）
        ("group_cross_civ.py", path) if scope == "world" else ("noop.py", path),
        # 人物按生卒年归位到正确的时期
        ("reassign_figures.py", path),
        # 少数条目的 periodId 在原始分片里就错了，自动归位纠正不了
        # （如汉高祖刘邦被标在战国），这里逐条按史实修正
        ("fix_figure_period_misc.py", path),
        # 规范化 id（原始分片里存在带空格/大写的畸形 id）
        ("fix_malformed_ids.py", path),
        # 事件名中文化（必须早于详情生成，否则模板会引用英文名）
        ("name_events.py", path),
        # 手写的高质量详情优先于模板生成
        ("apply_event_details.py", path),
        # 合并同名事件。必须放在 apply_event_details 之后、fill_event_detail
        # 之前——否则空壳事件会先被模板填上长段文字，在按内容择优时
        # 反而压过真实条目。
        ("merge_duplicate_events.py", path),
        # 清理合并带来的碎片化成就与错挂的名言
        ("clean_merged_residue.py", path),
        # 其余事件用模板补全 detail，保证详情页不留空
        ("fill_event_detail.py", path),
        # 占位人物补上中文名与身份，避免界面上出现英文 id。
        # 先做通用音译兜底，再用精确词典覆盖（顺序不能反）。
        ("translate_names.py", path),
        ("name_placeholders.py", path),
        ("fix_last_names.py", path),
        # 清理中英夹杂的翻译残留
        ("clean_mixed_text.py", path),
        # 统一人物 role 的写法，避免筛选栏出现同义重复项
        ("normalize_roles.py", path),
        # 清理 alias 里与名称重复的部分
        ("clean_alias.py", path),
        # 从已有数据推导补全人物与事件之间的关联
        ("build_relations.py", path),
        # 为「年份被填成时期起始年」的事件补上真实年份。
        # 必须放在所有会写 dateText 的步骤之后，否则会被回写覆盖。
        ("fix_collapsed_years.py", path),
        # 清理占位数据留下的英文 role 与重复词
        ("polish_text.py", path),
        # 最后一步：把所有 summary 收进校验器的长度区间，
        # 只用已有字段补足，不编写新内容
        ("fit_text_length.py", path),
    ]
    for script, *args in steps:
        out = run(script, *args)
        line = [l for l in out.splitlines() if l.strip()]
        print(f"  {script}: {line[-1] if line else '(no output)'}")

    err, warn = validate(path)
    print(f"\n=> {path}: ERROR={err}  WARN={warn}")

    if err:
        print("\n未清零，剩余错误：")
        out = run("validate_data.py", path)
        for line in out.splitlines():
            if "[ERROR]" in line:
                print("   " + line.strip())
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
