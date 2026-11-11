"""发版工具：把「改版本号 → 构建 → 打 tag → 发 Release」固化成一条命令。

用法：
    python tools/release.py 1.1.1                     # 修订号，缺陷修复
    python tools/release.py 1.2.0                     # 次版本号，新增功能或内容
    python tools/release.py 2.0.0 --dry-run           # 只检查不执行
    python tools/release.py 1.0.0 --project science-atlas   # 指定项目

它会依次完成：
1. 校验版本号合法，并检查与当前版本的关系（必须是递增）
2. 把 appVersion / appVersionCode 写进 build.gradle.kts
3. 同步 VERSION 文件
4. 构建 release APK，产物落在 <项目>/dist/<产物前缀>-v<版本>.apk
5. 提交并打 annotated tag
6. 创建 GitHub Release 并上传 APK

**纪律**：已发布的版本不允许覆盖。每次发版都升版本号，
versionCode 同步递增，否则 Android 不会把新包识别为升级。

多项目说明
----------
仓库里有多个可发版的 Android 项目，清单见 ``tools/projects.py``。
默认操作 history-atlas（保持既有行为不变），
``--project <key>`` 可切到别的项目。
"""
import argparse
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from projects import PROJECTS, ROOT, get_project, read_text, tag_for  # noqa: E402

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# 默认项目：保持历史行为——不带 --project 时操作 history-atlas。
DEFAULT_PROJECT = "history-atlas"


def run(cmd, cwd=ROOT, capture=True):
    """执行命令。失败时打印输出并中止。"""
    # Windows 上 gradlew.bat 是批处理文件，必须经由 shell 才能执行
    use_shell = os.name == "nt" and any(
        c.lower().endswith((".bat", ".cmd")) for c in cmd)
    r = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True,
                       encoding="utf-8", errors="replace", shell=use_shell)
    if r.returncode != 0:
        out = (r.stdout or "") + (r.stderr or "")
        print(out[-4000:])
        raise SystemExit(f"命令失败：{' '.join(cmd)}")
    return (r.stdout or "") + (r.stderr or "")


def current_version(project):
    s = read_text(project.build_gradle)
    m = re.search(r'val\s+appVersion\s*=\s*"([^"]+)"', s)
    return m.group(1) if m else None


def current_version_code(project):
    s = read_text(project.build_gradle)
    m = re.search(r"val\s+appVersionCode\s*=\s*(\d+)", s)
    return int(m.group(1)) if m else None


def bump_code(new_ver, old_ver, old_code):
    """按语义化版本规则推导新的 versionCode。

    主版本号变 → code 跳 1000（预留大版本空间）
    次版本号变 → code 跳 100
    仅修订号变 → code + 1
    """
    o = SEMVER.match(old_ver)
    n = SEMVER.match(new_ver)
    if not o or not n:
        return old_code + 1
    omaj, omin, opat = map(int, o.groups())
    nmaj, nmin, npat = map(int, n.groups())
    if nmaj > omaj:
        return old_code + 1000
    if nmin > omin:
        return old_code + 100
    if npat > opat:
        return old_code + 1
    return old_code + 1


def write_version(project, new_ver, new_code):
    s = read_text(project.build_gradle)
    s2 = re.sub(r'val\s+appVersion\s*=\s*"[^"]*"',
                f'val appVersion = "{new_ver}"', s)
    s2 = re.sub(r"val\s+appVersionCode\s*=\s*\d+",
                f"val appVersionCode = {new_code}", s2)
    io.open(project.build_gradle, "w", encoding="utf-8").write(s2)
    vf = os.path.join(ROOT, project.version_file)
    os.makedirs(os.path.dirname(vf), exist_ok=True)
    io.open(vf, "w", encoding="utf-8").write(new_ver + "\n")
    return s != s2


def check_changelog(project, new_ver):
    """检查 CHANGELOG 里是否已写入该版本的段落。"""
    path = os.path.join(ROOT, project.changelog)
    if not os.path.exists(path):
        return False
    return f"## v{new_ver}" in read_text(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="目标版本号，如 1.1.1")
    ap.add_argument("--project", default=DEFAULT_PROJECT,
                    help=f"项目 key（默认 {DEFAULT_PROJECT}），可选："
                         f"{', '.join(p.key for p in PROJECTS)}")
    ap.add_argument("--dry-run", action="store_true", help="只检查不改动")
    ap.add_argument("--no-build", action="store_true", help="跳过构建")
    ap.add_argument("--no-push", action="store_true", help="不推送远端")
    ap.add_argument("--notes", help="Release 说明文件路径")
    args = ap.parse_args()

    try:
        project = get_project(args.project)
    except KeyError as e:
        raise SystemExit(str(e))

    new_ver = args.version
    if not SEMVER.match(new_ver):
        raise SystemExit(f"版本号不合法：{new_ver}（应为 主.次.修订，如 1.2.0）")

    old_ver = current_version(project)
    old_code = current_version_code(project)
    if not old_ver or old_code is None:
        raise SystemExit(f"读不到 {project.key} 的当前版本号")

    # 目标版本与磁盘上的一致（上次发版中断留下的半成品）时，
    # versionCode 沿用磁盘上的值，避免重复递增。
    if old_ver == args.version:
        new_code = old_code
    else:
        new_code = bump_code(args.version, old_ver, old_code)

    tag = tag_for(project, new_ver)
    apk = project.apk_path(new_ver)

    print(f"项目：{project.name}（{project.key}）")
    print(f"当前版本：v{old_ver}（versionCode {old_code}）")
    print(f"目标版本：v{new_ver}（versionCode {new_code}）")
    print(f"目标 tag：{tag}")

    # --- 前置检查 ---
    # 已被发布过的版本不允许覆盖。判断依据是「有没有对应的 tag」，
    # 而不是「磁盘上写的是什么」——上一次发版若中途失败，
    # 版本号可能已写入但 tag 未打，这种情况要允许继续。
    already_tagged = bool(run(["git", "tag", "-l", tag]).strip())

    if already_tagged:
        raise SystemExit(
            f"{tag} 已经打过 tag，不允许覆盖。\n"
            "内容有变更就必须升版本号。请换一个更高的版本号。")

    if old_ver == new_ver and not already_tagged:
        # 版本号已是目标值但没打 tag：上次发版中断了，继续往下走
        print(f"（版本号已是 {new_ver}，继续完成剩余步骤）")
    elif old_ver == new_ver:
        raise SystemExit(
            f"版本号未变（{new_ver}）。\n"
            "已发布的版本不允许覆盖——内容有变更就必须升版本号。")

    if args.dry_run:
        print("\n[dry-run] 将执行：")
        print(f"  1. {project.dir}/app/build.gradle.kts → "
              f"appVersion={new_ver}, appVersionCode={new_code}")
        print(f"  2. {project.version_file} → {new_ver}")
        print(f"  3. 构建 {project.apk_name(new_ver)}")
        print(f"  4. git commit + tag {tag}")
        print(f"  5. gh release create {tag}")
        if not check_changelog(project, new_ver):
            print(f"\n  ⚠ {project.changelog} 里还没有「## v{new_ver}」段落")
        return

    # --- 1. 写版本号 ---
    changed = write_version(project, new_ver, new_code)
    print(f"[1/5] 版本号已写入（build.gradle.kts {'有' if changed else '无'}改动，VERSION 同步）")

    # --- 2. 检查 CHANGELOG ---
    if not check_changelog(project, new_ver):
        print(f"[2/5] ⚠ {project.changelog} 缺少「## v{new_ver}」段落，请补充后重跑")
        raise SystemExit(1)
    print(f"[2/5] {project.changelog} 已含 v{new_ver} 段落")

    # --- 3. 构建 ---
    if args.no_build:
        print("[3/5] 跳过构建")
    else:
        print("[3/5] 构建 release APK…")
        gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"
        run([gradlew, ":app:assembleRelease"], cwd=project.root)
        if not os.path.exists(apk):
            raise SystemExit(f"产物不存在：{apk}")
        print(f"      产物：{apk}（{os.path.getsize(apk):,} 字节）")

    # --- 4. 提交与打 tag ---
    print("[4/5] 提交并打 tag…")
    run(["git", "add", "-A"])
    status = run(["git", "status", "--porcelain"])
    if status.strip():
        msg = f"release({project.key}): v{new_ver}"
        run(["git", "commit", "-m", msg])
    else:
        print("      工作区无改动，跳过提交")
    run(["git", "tag", "-a", tag, "-m", f"{project.name} v{new_ver} 发布"])

    # --- 5. 推送与 Release ---
    print("[5/5] 推送并创建 Release…")
    if not args.no_push:
        # 分支与 tag 必须一条命令一起推。
        # 分两次推会留出竞态窗口：CI 由 main 的推送触发，但那一刻 tag 还没到远端，
        # 门禁的「检查是否有未发布的改动」就会把刚发布的这次提交判成
        # 「有 1 个提交尚未发布」并失败。一条命令推送时两个 ref 同时更新，
        # CI 启动即可看到 tag。
        run(["git", "push", "origin", "main", tag])

    title = project.release_title(new_ver)
    notes = args.notes
    if notes and os.path.exists(notes):
        run(["gh", "release", "create", tag, apk,
             "--title", title, "--notes-file", notes])
    else:
        run(["gh", "release", "create", tag, apk,
             "--title", title,
             "--notes", f"{title}。详见 {project.changelog}。"])

    url = run(["gh", "release", "view", tag, "--json", "url",
               "--template", "{{.url}}"]).strip()
    print(f"\n完成：{url}")


if __name__ == "__main__":
    main()
