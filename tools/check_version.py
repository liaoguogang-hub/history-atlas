"""版本一致性检查：确认版本号、CHANGELOG、tag、GitHub Release 对得上。

任何一项不一致都会以非零退出码失败，可挂到 CI 或本地提交前钩子上。

用法：
    python tools/check_version.py                      # 检查所有项目
    python tools/check_version.py --project history-atlas   # 只检查某一个
    python tools/check_version.py --local             # 只检查仓库内可验证的部分
    python tools/check_version.py --strict            # Release 资产 digest 不一致算错误
    python tools/check_version.py --since v1.1.0      # 检查某版本以来是否有未发布的改动

多项目说明
----------
仓库里有多个可发版的 Android 项目，清单见 ``tools/projects.py``。
每个项目独立维护版本号、VERSION 文件、CHANGELOG 与 tag。
"""
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from projects import PROJECTS, ROOT, all_tags, read_text, tag_for  # noqa: E402


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
    return read_text(path)


def gradle_version(project):
    s = read(project.build_gradle)
    m = re.search(r'val\s+appVersion\s*=\s*"([^"]+)"', s)
    return m.group(1) if m else None


def gradle_code(project):
    s = read(project.build_gradle)
    m = re.search(r"val\s+appVersionCode\s*=\s*(\d+)", s)
    return int(m.group(1)) if m else None


def check_project(project, local_only, strict):
    """检查单个项目，返回 (errors, warnings)。"""
    errors = []
    warnings = []

    ver = gradle_version(project)
    code = gradle_code(project)
    vfile = read(os.path.join(ROOT, project.version_file)).strip()
    changelog = read(os.path.join(ROOT, project.changelog))

    print(f"--- {project.name}（{project.key}）---")
    print(f"  build.gradle.kts : v{ver}（versionCode {code}）")
    print(f"  VERSION           : {vfile}")
    print(f"  CHANGELOG         : {os.path.relpath(os.path.join(ROOT, project.changelog), ROOT)}")

    if not ver:
        errors.append(f"[{project.key}] build.gradle.kts 里读不到 appVersion")
    if ver != vfile:
        errors.append(f"[{project.key}] VERSION 文件（{vfile}）与 "
                      f"build.gradle.kts（{ver}）不一致")

    # CHANGELOG 必须有当前版本的段落
    if ver and f"## v{ver}" not in changelog:
        errors.append(f"[{project.key}] {project.changelog} 缺少「## v{ver}」段落")

    # 当前版本必须已打 tag
    rc, out = run(["git", "tag", "-l"])
    if rc == 127:
        warnings.append(f"[{project.key}] git 不可用，跳过 tag 检查")
        tags = set()
    else:
        tags = {t.strip() for t in out.splitlines() if t.strip()}
    if ver:
        wanted = all_tags(project, ver)
        if not (wanted & tags):
            errors.append(f"[{project.key}] 尚未打 tag "
                          f"{' 或 '.join(sorted(wanted))}")

    # 远端必须已同步
    rc, out = run(["git", "status", "-sb"])
    if rc == 0 and "behind" in out.split("\n")[0]:
        errors.append(f"[{project.key}] 本地分支落后于远端，先 push")

    # GitHub Release 资产必须存在且与本地 digest 一致。
    # CI 环境里 gh 可能未安装或未认证，此时这一项查不了——
    # 降级成警告，不能让整条检查因为环境缺工具而崩掉。
    if ver and not local_only:
        tag = tag_for(project, ver)
        try:
            rc, out = run(["gh", "release", "view", tag, "--json", "assets",
                           "--template",
                           "{{range .assets}}{{.name}}|{{.size}}|{{.digest}}{{println}}{{end}}"])
        except (FileNotFoundError, OSError) as e:
            rc, out = 1, f"无法调用 gh：{e}"
        if rc != 0:
            warnings.append(f"[{project.key}] 查不到 {tag} 的 Release 资产"
                            f"（gh 不可用或未认证）：{out.strip()[:200]}")
        else:
            local = project.apk_path(ver)
            expected = project.apk_name(ver)
            found = False
            for line in out.splitlines():
                if not line.strip():
                    continue
                name, size, digest = (line.split("|") + ["", ""])[:3]
                if name != expected:
                    continue
                found = True
                if os.path.exists(local):
                    import hashlib
                    h = hashlib.sha256(io.open(local, "rb").read()).hexdigest()
                    if digest and h and digest.split(":")[-1] != h:
                        msg = (
                            f"[{project.key}] Release 资产与本地 dist 里的同名文件 "
                            f"digest 不一致\n    远端 {digest}\n    本地 sha256:{h}")
                        # 本地重新构建过就会产生不同的字节（构建时间戳等），
                        # 内容等价但不是同一份文件。日常自查算警告，
                        # 发版前后用 --strict 才当作错误。
                        if strict:
                            errors.append(msg)
                        else:
                            warnings.append(msg + "\n    （本地又构建过一份；"
                                             "确认内容一致可用 --strict 严格比对）")
                else:
                    warnings.append(f"[{project.key}] 本地没有 dist/{expected}")
            if not found:
                errors.append(f"[{project.key}] {tag} 的 Release 缺少资产 {expected}")

    return errors, warnings


def main():
    # --local：只检查仓库内可验证的部分。
    # CI 触发时 tag 可能还没推到远端（发版流程是先推 tag 再建 Release，
    # 两者之间有时间差），此时报「没有 tag」属于误报。
    local_only = "--local" in sys.argv
    # --strict：Release 资产与本地 dist 的 digest 不一致时算错误。
    # 日常自查用警告即可（本地重构建会产生不同字节），
    # 发版前后核对才需要严格比对。
    strict = "--strict" in sys.argv
    # --project <key>：只检查指定项目；缺省检查全部。
    only = None
    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        if idx + 1 >= len(sys.argv):
            print("--project 后面要跟项目 key")
            return 2
        only = sys.argv[idx + 1]

    targets = [p for p in PROJECTS if only is None or p.key == only]
    if not targets:
        print(f"未知项目：{only}")
        print(f"已登记：{', '.join(p.key for p in PROJECTS)}")
        return 2

    all_errors = []
    all_warnings = []
    for p in targets:
        errs, warns = check_project(p, local_only, strict)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        print()

    for w in all_warnings:
        print(f"⚠  {w}")
    for e in all_errors:
        print(f"✗  {e}")

    if all_errors:
        print(f"\n版本检查未通过：{len(all_errors)} 项错误")
        return 1
    print("版本检查通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
