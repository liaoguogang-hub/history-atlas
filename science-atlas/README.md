# 科学图鉴 ScienceAtlas

> 地理 · 天文 · 物理 · 化学 —— 四门自然科学，一条时间线。
> 纯离线 Android App，无网络权限，内容随应用打包。

本项目模仿 [`history-atlas`](../history-atlas)（历史图鉴）的架构与视觉语言，
把「朝代 / 历史事件 / 人物」三组实体映射为自然科学语境下的
「**分期 / 发现事件 / 科学家**」。

---

## 1. 功能

| 页面 | 说明 |
|---|---|
| **首页** | 四学科切换（地理 / 天文 / 物理 / 化学）+ 内容统计 + 功能入口 |
| **分期总览** | 分块年表树：左侧阶段脊柱 + 右侧分期色块，可下钻到三级 |
| **时间轴** | 横向可缩放时间轴，捏合缩放 / 拖动平移，按重要度分层的事件标记 |
| **科学家志** | 按身份筛选 + 按分期分组浏览 |
| **发现流** | 按时间与分类浏览全部学科事件 |
| **搜索** | 跨分期 / 事件 / 科学家三类实时过滤，命中关键词高亮 |
| **四科对照** | 任选两门学科并排，按同一「聚焦年代」同步高亮与滚动 |
| **详情页** | 分期详情 / 事件详情 / 科学家详情（生平、成就、名言、关联跳转） |

**四个学科**

| scope | 学科 | 典型分期 |
|---|---|---|
| `geo` | 地理 | 地质年代、地理大发现时代、板块构造时代、气候科学时期 |
| `astro` | 天文学 | 观测手段演进、宇宙学模型演化、太阳系与深空观测 |
| `physics` | 物理学 | 经典力学、电磁学、量子力学、相对论、核物理 |
| `chem` | 化学 | 炼金术、原子论、周期表时代、有机化学、结构化学 |

---

## 2. 架构

```
science-atlas/
├── app/src/main/java/com/scienceatlas/app/
│   ├── MainActivity.kt              单 Activity 入口
│   ├── data/
│   │   ├── Models.kt                数据模型（Period / Event / Figure / EventCategory）
│   │   └── ScienceRepository.kt      懒加载 + 索引 + 引用容错 + 搜索 + 分期分组
│   └── ui/
│       ├── AppNavHost.kt             导航图（scope 走 query 参数）
│       ├── MainViewModel.kt          学科切换状态 + 时间轴视窗记忆
│       ├── components/               通用组件（徽章/星级/头像/色块/时间轴画布）
│       ├── screens/                  10 个页面
│       └── theme/                    配色 / 排版 / 形状
├── app/src/test/                     47 个单元测试（纯 JVM）
├── data-science/                     ← 数据源（由 syncData 任务同步进 assets）
│   ├── SCHEMA.md                     数据契约
│   ├── geo.json  astro.json  physics.json  chem.json
└── tools/sci_content/                数据生成与校验脚本
```

**技术栈**：Kotlin 2.1.21 · Jetpack Compose (BOM 2024.10.01) · Material 3 ·
Navigation Compose · kotlinx.serialization · Gradle 8.14.2 / AGP 8.11.1 ·
compileSdk 35 / minSdk 24 / targetSdk 35

**离线**：数据打包在 `assets/data/*.json`，无网络权限声明。

---

## 3. 构建

```powershell
# 单元测试
.\gradlew.bat :app:testReleaseUnitTest --offline

# 构建 release APK（自动同步数据 + 输出到 dist/）
.\gradlew.bat :app:assembleRelease --offline
```

产物：`dist/ScienceAtlas-v1.0.0.apk`

> release 使用 **debug 密钥**签名，产物可直接安装，适合自行分发，不适合上架。

### 数据同步

`syncData` 任务在每次 `preBuild` 前把 `data-science/*.json` 复制到
`app/src/main/assets/data/`。源文件缺失时**只警告并跳过**，不会让构建失败。

```powershell
.\gradlew.bat :app:syncData
```

可用 `-PsyncDataSource=<dir>` / `-PsyncDataTarget=<dir>` 覆盖路径。

---

## 4. 数据契约

详见 [`data-science/SCHEMA.md`](../data-science/SCHEMA.md)。

要点：
- 顶层 `version` / `scope` / `periods` / `events` / `figures`
- `period.parentId` / `event.periodId` / `figure.periodId` 单向引用，允许悬空（App 容错剔除）
- 顶层分期的 `tags` 含 `编年主干` → 强制进入主干分组
- `tags` 含 `专题` / `跨尺度`，或 `colorKey = "purple"` → 归入「专题补充」组

校验脚本：

```powershell
python tools\sci_content\validate_sci.py
```

---

## 5. 与 history-atlas 的差异

| 方面 | history-atlas | science-atlas |
|---|---|---|
| 分支 | 中国史 / 世界史 | 地理 / 天文 / 物理 / 化学 |
| `period` 语义 | 朝代 | 分期 / 理论体系 / 尺度层级 |
| `event` 语义 | 历史事件 | 发现 / 理论提出 / 技术突破 |
| `figure` 语义 | 人物 | 科学家 |
| 对照页 | 中国史 vs 世界史 | 任选两门学科并排 |
| 学科切换控件 | 两段横排 | 两行两列（窄屏可读） |
| 配色 | 马卡龙暖色 | 冷调理性色，四学科各有主色 |
| 分期分组 bug | **存在**（同一分期同时进两组） | 已修复并加回归测试 |

### 修复的上游缺陷

`history-atlas` 的 `splitByChronology` 中，`wrappers + rest` 会让上位分期被**处理两次**
——先进主干、再因与自己冲突被踢进补充组，最终同时出现在两组里。
该缺陷使 `history-atlas` 自身的 5 个单元测试失败。

本项目改为：被完全包裹的分期显式归入补充组，候选序列去重后只处理一次，
并新增 `同一分期不会同时出现在两组` 回归测试。47 个测试全部通过。
