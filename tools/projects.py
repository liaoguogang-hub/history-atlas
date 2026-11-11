"""多项目登记表：把「仓库里有哪些 App、各自叫什么、版本号写在哪」集中在一处。

背景
----
这个仓库同时放着多个互不相关的 Android 项目：

- ``history-atlas``  历史图鉴（中国史 / 世界史）
- ``science-atlas``  科学图鉴（地理 / 天文 / 物理 / 化学）

早期 ``tools/check_version.py`` 与 ``tools/release.py`` 把项目路径写死成
``history-atlas``，加第二个项目时就得改一遍工具、再改一遍 CI。
本模块把「项目清单」抽出来，工具按清单工作——加新项目只改这一处。

每个项目登记项包含：

``key``       项目标识，同时也是 tag 的前缀（``v1.2.3`` → ``history-atlas-v1.2.3``）
``name``      中文名，用于 Release 标题与提示文案
``dir``       项目在仓库根下的目录名
``apk_prefix`` 产物文件名（不含版本号）前缀，如 ``HistoryAtlas``
``version_file`` 项目自己的 VERSION 文件路径（相对仓库根）
``changelog`` 项目自己的 CHANGELOG 路径（相对仓库根）
"""

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
    """一个可发版项目的登记信息。"""

    def __init__(self, key, name, directory, apk_prefix, app_id,
                 version_file, changelog):
        self.key = key
        self.name = name
        self.dir = directory
        self.apk_prefix = apk_prefix
        self.app_id = app_id
        self.version_file = version_file
        self.changelog = changelog

    # ---- 路径 ----

    @property
    def root(self):
        return os.path.join(ROOT, self.dir)

    @property
    def build_gradle(self):
        return os.path.join(self.root, "app", "build.gradle.kts")

    @property
    def dist_dir(self):
        return os.path.join(self.root, "dist")

    # ---- 版本相关文件名 ----

    def tag(self, version):
        """该项目某版本对应的 git tag 名。

        带项目前缀是为了让两个项目的版本号互不干扰——
        否则 history-atlas 的 v1.1.5 和 science-atlas 的 v1.1.5 会抢同一个 tag。
        """
        return f"{self.key}-v{version}"

    def apk_name(self, version):
        return f"{self.apk_prefix}-v{version}.apk"

    def apk_path(self, version):
        return os.path.join(self.dist_dir, self.apk_name(version))

    def release_title(self, version):
        return f"{self.name} v{version}"


# 仓库里的项目清单。**加新项目只改这里。**
PROJECTS = [
    Project(
        key="history-atlas",
        name="历史图鉴",
        directory="history-atlas",
        apk_prefix="HistoryAtlas",
        app_id="com.historyatlas.app",
        version_file="VERSION",
        changelog="CHANGELOG.md",
    ),
    Project(
        key="science-atlas",
        name="科学图鉴",
        directory="science-atlas",
        apk_prefix="ScienceAtlas",
        app_id="com.scienceatlas.app",
        version_file="science-atlas/VERSION",
        changelog="science-atlas/CHANGELOG.md",
    ),
]

# 保持历史行为：history-atlas 的 tag 是裸 ``v1.1.5``（不带项目前缀），
# 已经打过很多个，改名会打断既有 Release 与 CI 的关联。
#
# 所以规则是：**第一个项目沿用裸 tag，后续项目带前缀**。
# 这样既不动 history-atlas 的历史，又让新增项目有独立命名空间。
LEGACY_BARE_TAG_KEYS = {"history-atlas"}


def tag_for(project, version):
    """给出该项目的实际 tag 名。"""
    if project.key in LEGACY_BARE_TAG_KEYS:
        return f"v{version}"
    return project.tag(version)


def all_tags(project, version):
    """该版本可能用到的所有 tag 名（历史兼容时不止一个）。"""
    names = {tag_for(project, version)}
    names.add(project.tag(version))
    return names


def get_project(key):
    for p in PROJECTS:
        if p.key == key:
            return p
    raise KeyError(f"未知项目：{key}（已登记：{', '.join(p.key for p in PROJECTS)}）")


def read_text(path):
    if not os.path.exists(path):
        return ""
    return io.open(path, encoding="utf-8").read()
