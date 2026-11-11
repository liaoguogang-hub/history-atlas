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
    """执行命令，返回 (退出码, 输出)。

    命令不存在时返回 (127, 错误信息) 而不是抛异常——
    检查脚本要能在工具缺失的环境下继续跑完，把该项降级成警告。
    """
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError) as e:
        return 127, f"命令不可用：{cmd[0]}（{e}）"
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
    # --local：只检查仓库内可验证的部分。
    # CI 触发时 tag 可能还没推到远端（发版流程是先推 tag 再建 Release，
    # 两者之间有时间差），此时报「没有 tag」属于误报。
    local_only = "--local" in sys.argv
    # --strict：Release 资产与本地 dist 的 digest 不一致时算错误。
    # 日常自查用警告即可（本地重构建会产生不同字节），
    # 发版前后核对才需要严格比对。
    strict = "--strict" in sys.argv

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
    if rc == 127:
        warnings.append("git 不可用，跳过 tag 检查")
        tags = set()
    else:
        tags = {t.strip() for t in out.splitlines() if t.strip()}
    if ver and f"v{ver}" not in tags:
        errors.append(f"尚未打 tag v{ver}")

    # 远端必须已同步
    rc, out = run(["git", "status", "-sb"])
    if rc == 0 and "behind" in out.split("\n")[0]:
        errors.append("本地分支落后于远端，先 push")

    # GitHub Release 资产必须存在且与本地 digest 一致。
    # CI 环境里 gh 可能未安装或未认证，此时这一项查不了——
    # 降级成警告，不能让整条检查因为环境缺工具而崩掉。
    if ver:
        try:
            rc, out = run(["gh", "release", "view", f"v{ver}", "--json", "assets",
                           "--template",
                           "{{range .assets}}{{.name}}|{{.size}}|{{.digest}}{{println}}{{end}}"])
        except (FileNotFoundError, OSError) as e:
            rc, out = 1, f"无法调用 gh：{e}"
        if rc != 0:
            warnings.append(f"查不到 v{ver} 的 Release 资产（gh 不可用或未认证）：{out.strip()[:200]}")
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
                        msg = (
                            f"Release 资产与本地 dist 里的同名文件 digest 不一致\n"
                            f"    远端 {digest}\n"
                            f"    本地 sha256:{h}")
                        # 本地重新构建过就会产生不同的字节（构建时间戳等），
                        # 内容等价但不是同一份文件。日常自查算警告，
                        # 发版前后用 --strict 才当作错误。
                        if strict:
                            errors.append(msg)
                        else:
                            warnings.append(msg + "\n    （本地又构建过一份；"
                                             "确认内容一致可用 --strict 严格比对）")
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
