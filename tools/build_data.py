"""完整数据流水线：分片 → 合并 → 修复 → 校验。

用法:
    python tools/build_data.py            # 合并两个 scope 并校验
    python tools/build_data.py china      # 只处理中国史
    python tools/build_data.py world      # 只处理世界史
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
TMP = os.path.join(ROOT, "data", ".tmp")

SCOPES = {
    "china": {
        "shards": [
            os.path.join(TMP, "china_periods.json"),
            os.path.join(TMP, "evdata_*.json"),
            os.path.join(TMP, "figdata_*.json"),
        ],
        "out": os.path.join(ROOT, "data", "china.json"),
    },
    "world": {
        "shards": [
            os.path.join(TMP, "world_*.json"),
        ],
        "out": os.path.join(ROOT, "data", "world.json"),
    },
}


def run(script, *args):
    cmd = [sys.executable, os.path.join(TOOLS, script)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0 and "Traceback" in out:
        print(f"  !! {script} failed:")
        for line in out.splitlines()[-6:]:
            print("     " + line)
    return out


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def expand(patterns):
    out = []
    for p in patterns:
        if "*" in p:
            out.extend(sorted(glob.glob(p)))
        elif os.path.exists(p):
            out.append(p)
    return out


def main():
    targets = sys.argv[1:] or ["china", "world"]
    overall_ok = True

    for scope in targets:
        cfg = SCOPES[scope]
        print(f"\n{'=' * 60}\n{scope.upper()}\n{'=' * 60}")

        shards = expand(cfg["shards"])
        if not shards:
            print("  没有找到分片文件")
            overall_ok = False
            continue

        # 合并之前先规范分片里含义不清的人物 id。
        # 这一步直接改写分片文件，因此必须在 merge_shards 之前调用。
        if scope == "china":
            for script in ("normalize_figure_ids.py", "resolve_shard_refs.py"):
                r = sh([sys.executable, os.path.join(TOOLS, script)])
                for line in (r.stdout or "").splitlines():
                    if line.strip():
                        print("  " + line)

        cmd = [sys.executable, os.path.join(TOOLS, "merge_shards.py"),
               "--scope", scope, "--out", cfg["out"]] + shards
        r = sh(cmd)
        for line in (r.stdout or "").splitlines():
            if line.strip():
                print("  " + line)

        # 中国史必须先完整修复：世界史要从中借用真实人物内容
        if scope == "china":
            out = run("fix_pipeline.py", cfg["out"], scope)
            for line in out.splitlines():
                if line.startswith("=>"):
                    print("  " + line)
                elif "[ERROR]" in line:
                    print("  " + line.strip())
            m = re.search(r"ERROR=(\d+)\s+WARN=(\d+)", out)
            if not m or int(m.group(1)) != 0:
                overall_ok = False
            continue

        # 世界史：先跑一遍基础修复，再从中国史借入真实人物内容，
        # 最后再跑一遍修复（借来的内容需要再校正 periodId 与引用）。
        out = run("fix_pipeline.py", cfg["out"], scope)
        for line in out.splitlines():
            if line.startswith("=>"):
                print("  " + line)

        out = run("copy_cn_to_world.py")
        for line in out.splitlines():
            if line.strip():
                print("  " + line)

        out = run("fix_pipeline.py", cfg["out"], scope)
        for line in out.splitlines():
            if line.startswith("=>"):
                print("  " + line)
            elif "[ERROR]" in line:
                print("  " + line.strip())

        m = re.search(r"ERROR=(\d+)\s+WARN=(\d+)", out)
        if not m or int(m.group(1)) != 0:
            overall_ok = False

    print()
    if overall_ok:
        print("全部 scope 校验通过 (ERROR = 0)")
    else:
        print("仍有未通过项")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
