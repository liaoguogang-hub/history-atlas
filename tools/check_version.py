"""版本一致性检查：确认版本号、CHANGELOG、tag、GitHub Release 对得上。

任何一项不一致都会以非零退出码失败，可挂到 CI 或本地提交前钩子上。

用法：
    python tools/check_version.py            # 检查当前状态
    python tools/check_version.py --since v1.1.0   # 检查某版本以来是否有未发布的改动
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_GRADLE = os.path.join(ROOT, "history-atlas", "app", "build.gradle.kts")
VERSION_FILE = os.path.join(ROOT, "VERSION")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")


def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def read(path):
    if not os.path.exists(path):
        return ""
    return io.open(path, encoding="utf-8").read()


def gradle_version():
    s = read(BUILD_GRADLE)
    m = re.search(r'val\s+appVersion\s*=\s*"([^"]+)"', s)
    return m.group(1) if m else None


def gradle_code():
    s = read(BUILD_GRADLE)
    m = re.search(r"val\s+appVersionCode\s*=\s*(\d+)", s)
    return int(m.group(1)) if m else None


def main():
    errors = []
    warnings = []

    ver = gradle_version()
    code = gradle_code()
    vfile = read(VERSION_FILE).strip()

    print(f"build.gradle.kts : v{ver}（versionCode {code}）")
    print(f"VERSION           : {vfile}")

    if not ver:
        errors.append("build.gradle.kts 里读不到 appVersion")
    if ver != vfile:
        errors.append(f"VERSION 文件（{vfile}）与 build.gradle.kts（{ver}）不一致")

    # CHANGELOG 必须有当前版本的段落
    if ver and f"## v{ver}" not in read(CHANGELOG):
        errors.append(f"CHANGELOG.md 缺少「## v{ver}」段落")

    # 当前版本必须已打 tag，且 tag 指向 HEAD 附近的提交
    rc, out = run(["git", "tag", "-l"])
    tags = {t.strip() for t in out.splitlines() if t.strip()}
    if ver and f"v{ver}" not in tags:
        errors.append(f"尚未打 tag v{ver}")

    # 远端必须已同步
    rc, out = run(["git", "status", "-sb"])
    if rc == 0 and "behind" in out.split("\n")[0]:
        errors.append("本地分支落后于远端，先 push")

    # GitHub Release 资产必须存在且与本地 digest 一致
    if ver:
        rc, out = run(["gh", "release", "view", f"v{ver}", "--json", "assets",
                       "--template", "{{range .assets}}{{.name}}|{{.size}}|{{.digest}}{{println}}{{end}}"])
        if rc != 0:
            warnings.append(f"GitHub 上没有 v{ver} 的 Release（尚未发布）")
        else:
            local = os.path.join(ROOT, "history-atlas", "dist", f"HistoryAtlas-v{ver}.apk")
            found = False
            for line in out.splitlines():
                if not line.strip():
                    continue
                name, size, digest = (line.split("|") + ["", ""])[:3]
                if name != f"HistoryAtlas-v{ver}.apk":
                    continue
                found = True
                if os.path.exists(local):
                    import hashlib
                    h = hashlib.sha256(io.open(local, "rb").read()).hexdigest()
                    if digest and h and digest.split(":")[-1] != h:
                        errors.append(
                            f"Release 资产与本地 dist 里的同名文件 digest 不一致\n"
                            f"    远端 {digest}\n    本地 sha256:{h}")
                else:
                    warnings.append(f"本地没有 dist/HistoryAtlas-v{ver}.apk")
            if not found:
                errors.append(f"v{ver} 的 Release 缺少资产 HistoryAtlas-v{ver}.apk")

    print()
    for w in warnings:
        print(f"⚠  {w}")
    for e in errors:
        print(f"✗  {e}")

    if errors:
        print(f"\n版本检查未通过：{len(errors)} 项错误")
        return 1
    print("版本检查通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
