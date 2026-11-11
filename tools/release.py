"""发版工具：把「改版本号 → 构建 → 打 tag → 发 Release」固化成一条命令。

用法：
    python tools/release.py 1.1.1              # 修订号，缺陷修复
    python tools/release.py 1.2.0              # 次版本号，新增功能或内容
    python tools/release.py 2.0.0 --dry-run    # 只检查不执行

它会依次完成：
1. 校验版本号合法，并检查与当前版本的关系（必须是递增）
2. 把 appVersion / appVersionCode 写进 build.gradle.kts
3. 同步 VERSION 文件
4. 构建 release APK，产物落在 dist/HistoryAtlas-v<版本>.apk
5. 提交并打 annotated tag
6. 创建 GitHub Release 并上传 APK

**纪律**：已发布的版本不允许覆盖。每次发版都升版本号，
versionCode 同步递增，否则 Android 不会把新包识别为升级。
"""
import argparse
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

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


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


def current_version():
    s = io.open(BUILD_GRADLE, encoding="utf-8").read()
    m = re.search(r'val\s+appVersion\s*=\s*"([^"]+)"', s)
    return m.group(1) if m else None


def current_version_code():
    s = io.open(BUILD_GRADLE, encoding="utf-8").read()
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


def write_version(new_ver, new_code):
    s = io.open(BUILD_GRADLE, encoding="utf-8").read()
    s2 = re.sub(r'val\s+appVersion\s*=\s*"[^"]*"',
                f'val appVersion = "{new_ver}"', s)
    s2 = re.sub(r"val\s+appVersionCode\s*=\s*\d+",
                f"val appVersionCode = {new_code}", s2)
    io.open(BUILD_GRADLE, "w", encoding="utf-8").write(s2)
    io.open(VERSION_FILE, "w", encoding="utf-8").write(new_ver + "\n")
    return s != s2


def check_changelog(new_ver):
    """检查 CHANGELOG 里是否已写入该版本的段落。"""
    if not os.path.exists(CHANGELOG):
        return False
    s = io.open(CHANGELOG, encoding="utf-8").read()
    return f"## v{new_ver}" in s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="目标版本号，如 1.1.1")
    ap.add_argument("--dry-run", action="store_true", help="只检查不改动")
    ap.add_argument("--no-build", action="store_true", help="跳过构建")
    ap.add_argument("--no-push", action="store_true", help="不推送远端")
    ap.add_argument("--notes", help="Release 说明文件路径")
    args = ap.parse_args()

    new_ver = args.version
    if not SEMVER.match(new_ver):
        raise SystemExit(f"版本号不合法：{new_ver}（应为 主.次.修订，如 1.2.0）")

    old_ver = current_version()
    old_code = current_version_code()

    # 目标版本与磁盘上的一致（上次发版中断留下的半成品）时，
    # versionCode 沿用磁盘上的值，避免重复递增。
    if old_ver == args.version:
        new_code = old_code
    else:
        new_code = bump_code(args.version, old_ver, old_code)

    print(f"当前版本：v{old_ver}（versionCode {old_code}）")
    print(f"目标版本：v{new_ver}（versionCode {new_code}）")

    # --- 前置检查 ---
    # 已被发布过的版本不允许覆盖。判断依据是「有没有对应的 tag」，
    # 而不是「磁盘上写的是什么」——上一次发版若中途失败，
    # 版本号可能已写入但 tag 未打，这种情况要允许继续。
    already_tagged = bool(run(["git", "tag", "-l", f"v{new_ver}"]).strip())

    if already_tagged:
        raise SystemExit(
            f"v{new_ver} 已经打过 tag，不允许覆盖。\n"
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
        print(f"  1. build.gradle.kts → appVersion={new_ver}, appVersionCode={new_code}")
        print(f"  2. VERSION → {new_ver}")
        print(f"  3. 构建 dist/HistoryAtlas-v{new_ver}.apk")
        print(f"  4. git commit + tag v{new_ver}")
        print(f"  5. gh release create v{new_ver}")
        if not check_changelog(new_ver):
            print(f"\n  ⚠ CHANGELOG.md 里还没有「## v{new_ver}」段落")
        return

    # --- 1. 写版本号 ---
    changed = write_version(new_ver, new_code)
    print(f"[1/5] 版本号已写入（build.gradle.kts {'有' if changed else '无'}改动，VERSION 同步）")

    # --- 2. 检查 CHANGELOG ---
    if not check_changelog(new_ver):
        print(f"[2/5] ⚠ CHANGELOG.md 缺少「## v{new_ver}」段落，请补充后重跑")
        raise SystemExit(1)
    print(f"[2/5] CHANGELOG.md 已含 v{new_ver} 段落")

    # --- 3. 构建 ---
    if args.no_build:
        print("[3/5] 跳过构建")
        apk = os.path.join(ROOT, "history-atlas", "dist", f"HistoryAtlas-v{new_ver}.apk")
    else:
        print("[3/5] 构建 release APK…")
        gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"
        run([gradlew, ":app:assembleRelease"],
            cwd=os.path.join(ROOT, "history-atlas"))
        apk = os.path.join(ROOT, "history-atlas", "dist", f"HistoryAtlas-v{new_ver}.apk")
        if not os.path.exists(apk):
            raise SystemExit(f"产物不存在：{apk}")
        print(f"      产物：{apk}（{os.path.getsize(apk):,} 字节）")

    # --- 4. 提交与打 tag ---
    print("[4/5] 提交并打 tag…")
    run(["git", "add", "-A"])
    status = run(["git", "status", "--porcelain"])
    if status.strip():
        msg = f"release: v{new_ver}"
        run(["git", "commit", "-m", msg])
    else:
        print("      工作区无改动，跳过提交")
    run(["git", "tag", "-a", f"v{new_ver}", "-m", f"v{new_ver} 发布"])

    # --- 5. 推送与 Release ---
    print("[5/5] 推送并创建 Release…")
    if not args.no_push:
        run(["git", "push", "origin", "main"])
        run(["git", "push", "origin", f"v{new_ver}"])

    notes = args.notes
    if notes and os.path.exists(notes):
        run(["gh", "release", "create", f"v{new_ver}", apk,
             "--title", f"历史图鉴 v{new_ver}", "--notes-file", notes])
    else:
        run(["gh", "release", "create", f"v{new_ver}", apk,
             "--title", f"历史图鉴 v{new_ver}",
             "--notes", f"历史图鉴 v{new_ver}。详见 CHANGELOG.md。"])

    url = run(["gh", "release", "view", f"v{new_ver}", "--json", "url",
               "--template", "{{.url}}"]).strip()
    print(f"\n完成：{url}")


if __name__ == "__main__":
    main()
