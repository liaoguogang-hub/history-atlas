"""安装 git 钩子：把 .githooks/pre-commit 装到 .git/hooks/pre-commit。

Windows 的 Git for Windows 会用自带的 bash 执行无扩展名的钩子，
所以同一个 sh 脚本在所有平台通用。sh 脚本需要 shebang 与可执行位，
否则 git 报 "cannot spawn"。

钩子只在本地生效，不随仓库分发，别人 clone 后需要自己跑一次。
想让钩子跟着仓库走，在 .git/config 里设 core.hooksPath = .githooks。
"""
import os
import shutil
import stat
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, ".githooks")
GIT_HOOKS = os.path.join(ROOT, ".git", "hooks")


def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    os.makedirs(GIT_HOOKS, exist_ok=True)

    src = os.path.join(HOOKS, "pre-commit")
    if not os.path.exists(src):
        print("找不到 .githooks/pre-commit")
        return 1

    dst = os.path.join(GIT_HOOKS, "pre-commit")
    shutil.copyfile(src, dst)
    make_executable(dst)
    print("已安装钩子：.git/hooks/pre-commit")

    cmd_src = os.path.join(HOOKS, "pre-commit.cmd")
    if os.path.exists(cmd_src):
        shutil.copyfile(cmd_src, os.path.join(GIT_HOOKS, "pre-commit.cmd"))
        print("已安装钩子：.git/hooks/pre-commit.cmd")

    print("")
    print("完成。钩子会在以下情况拦截提交：")
    print("  代码或数据有改动，但 HEAD 已领先于最新版本 tag（说明有内容未发版）")
    print("")
    print("例外：纯文档改动不拦；版本号已与最新 tag 不同时（发版进行中）不拦")
    print("跳过方式：git commit --no-verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
