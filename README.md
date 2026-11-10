# 历史图鉴（History Atlas）

一款离线的**中国史 + 世界史**知识图谱 Android App。把静态的「朝代分块年表图」变成**可缩放、可搜索、可下钻、可对照**的交互式应用。

参考原型：维基百科《中国历史（消歧义）》的色块年表图 —— 本 App 复刻其视觉语言（马卡龙色块 + 时代脊柱 + 嵌套色块），并补齐静态图做不到的事：点开每个色块看详情、横向缩放时间轴、跨文明同时对照。

---

## 快速开始

### 从克隆构建

仓库不包含构建产物与同步后的 assets，克隆后按下面四步即可跑起来：

```powershell
git clone https://github.com/liaoguogang-hub/history-atlas.git
cd history-atlas

# 1. 一条命令完成：分片合并 → 数据修复 → 校验（目标 ERROR = 0）
python tools\build_data.py

# 2. 同步进 assets
powershell -ExecutionPolicy Bypass -File scripts\sync_data.ps1

# 3. 构建 APK（local.properties 由 Gradle 按本机 Android SDK 自动生成，
#    若未生成，手动写入 sdk.dir=你的 Android SDK 路径）
cd history-atlas
.\gradlew.bat :app:assembleDebug

# 4. 安装
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

产物：`history-atlas/app/build/outputs/apk/debug/app-debug.apk`（约 17.2 MB）

环境要求：JDK 17、Android SDK（compileSdk 35）、Python 3.9+。

### 构建 Release 包

```powershell
cd history-atlas
.\gradlew.bat :app:assembleRelease
```

R8 混淆压缩后自动复制到 `dist/HistoryAtlas-v<版本号>.apk`（约 2.0 MB，
比 debug 包小 8.5 倍，主要是剥掉了 material-icons-extended 中未使用的图标）。

- 产物名由 `app/build.gradle.kts` 顶部的 `appVersion` 派生，不会与 APK 内的
  `versionName` 漂移
- 使用 **debug 密钥**签名：产物可直接安装，无需另配 keystore
- `dist/` 与 `*.apk` 均在 `.gitignore` 中，产物不入库，通过 GitHub Release 分发
- R8 依赖 `app/proguard-rules.pro` 保留 kotlinx.serialization 的序列化器，
  否则数据无法反序列化（构建后请实际安装验证，不要只看编译通过）

### 发布新版本

1. 改 `app/build.gradle.kts` 顶部的 `appVersion` / `appVersionCode`
2. 同步 `VERSION` 文件、`CHANGELOG.md`、`README.md` 的规模统计
3. `.\gradlew.bat :app:assembleRelease`
4. 提交并打标签：`git tag -a vX.Y.Z`
5. `gh release create vX.Y.Z history-atlas/dist/HistoryAtlas-vX.Y.Z.apk`

### 直接安装

到 [Releases](https://github.com/liaoguogang-hub/history-atlas/releases) 下载 `HistoryAtlas-v1.1.0.apk`，
支持 Android 7.0（API 24）及以上。当前为 debug 密钥签名（R8 混淆的 release 构建），仅供自行分发。

### 版本管理

- **单一来源**：版本号只写在 `app/build.gradle.kts` 顶部的 `appVersion` 与 `appVersionCode`，
  `VERSION` 文件、dist 产物名与 Release 标签都由它派生
- **versionCode 必须递增**：否则 Android 不会把新包识别为升级，已安装旧版的用户收不到更新
- **发布三步**：改版本号 → 构建 → 打 tag 并发 Release
- **不覆盖已发布资产**：Release 一旦发布就不再改动其 APK，内容变更一律走新版本号
- 变更记录见 [CHANGELOG.md](CHANGELOG.md)，遵循语义化版本

无 shell 环境时的发布流程：

```powershell
# 1. 改 app/build.gradle.kts 的 appVersion / appVersionCode，同步 VERSION 文件
# 2. 构建
cd history-atlas
.\gradlew.bat :app:assembleRelease      # 自动输出到 dist/HistoryAtlas-v<版本>.apk
# 3. 打 tag 并发 Release
cd ..
git tag -a v1.1.0 -m "v1.1.0 ..."
gh release create v1.1.0 "history-atlas/dist/HistoryAtlas-v1.1.0.apk" --title "..." --notes-file ...
```

### 当前内容规模

| | 时期 | 事件 | 人物 | 人物传记均值 | 传记最短 | 成就均值 | 零关联人物 |
|---|---|---|---|---|---|---|---|
| 中国史 | 64 | 378 | 442 | 527 字 | 300 字 | 8.4 条 | 5 人 |
| 世界史 | 89 | 360 | 235 | 455 字 | 300 字 | 7.0 条 | 6 人 |

两个 scope 的校验结果均为 **ERROR = 0 / WARN = 0**，且无占位条目、无拉丁文残留、
**无短于 300 字的人物传记**、无模板化空壳事件。

人物内容的扩充前后对比：

| 指标 | 扩充前 | 扩充后 |
|---|---|---|
| 中国史传记均值 | 220 字 | **527 字** |
| 中国史传记不足 200 字 | 177 人 | **0 人** |
| 中国史成就平均条数 | 4.2 条 | **8.4 条** |
| 中国史有 5 条以上关联 | 14 人 | **342 人** |
| 中国史完全无关联 | 202 人 | **5 人** |
| 世界史传记均值 | 338 字 | **455 字** |
| 世界史有 5 条以上关联 | 12 人 | **108 人** |
| 世界史完全无关联 | 19 人 | **6 人** |

人物关联由 `build_relations.py` 从三个方向推导：同事件参与者互连、
事件正文提及人物、人物传记提及事件（后者用关键词匹配，
因为事件名往往很长，传记里不会逐字包含）。

世界史的 89 个时期里含一条「跨文明交流」专题线（1 个父时期 + 6 个时代子时期），
承载 104 个跨文明事件。

> 数据经过多轮清理：原始分片里同一个人物常被拆成多条
> （梁武帝萧衍 8 条、隋文帝杨坚 5 条、王猛 5 条），同一事件也常重复
> （九一八事变 3 条）。分别由 `merge_duplicate_figures.py` 与
> `merge_duplicate_events.py` 合并为一条，取内容最丰富的版本并合并关联。
> 另有「李昂/李昴」「李怀光×2」「鱼朝恩×2」等因生卒年冲突或错字而未被自动合并的
> 重复条目，由 `FORCE_MERGE` 与 `NAME_ALIAS` 机制处理。
>
> 另有 113 个事件与 40 余个人物条目是自动补引用时生成的空壳
> （摘要为固定模板、名字由 id 音译、年份被填成时期起始年），
> 已逐个补写真实内容；无法考据出处的条目由 `prune_fabricated.py` 连同引用一并删除。

---

## 功能一览

| 模块 | 说明 |
|---|---|
| **年表总览** | 分块年表树：左侧时代脊柱 + 右侧嵌套时期色块，色块高度按持续年数**平方根**映射，左列高度与右列精确对齐 |
| **时间轴** | 横向时间轴，顶部为朝代带、底部年代刻度（每 100 年一格），捏合缩放 / 拖动平移，事件标记按重要度分级，22 个分类可多选筛选，支持就地搜索 |
| **时期详情** | 色块 banner + 疆域/都城/人口/文化概况 + 子时期 + 关键人物 + 代表事件（可下钻到具体时期） |
| **事件详情** | 分类徽章 + 重要度星级 + 摘要 + 详细记述（可折叠）+ 涉及人物 + 相关事件 |
| **人物详情** | 头像 + 生卒 + 身份 + 生平 + 主要成就 + 名言引用 + 相关事件/相关人物 |
| **搜索** | 跨时期/事件/人物实时过滤，关键词高亮，支持从建议词直接搜 |
| **人物志** | 按时期（含子时期）+ 身份双重筛选，按时期分组，右上角按钮唤出就地搜索 |
| **事件流** | 按重要度分层、层内按编年排序，分类筛选 + 右上角按钮唤出就地搜索 |
| **中外对照** | 中国史与世界史并排，年代以 100 年为一档，点选后两侧各自滚动到对应朝代并高亮 |

### 交互细节

- **时间轴拖动方向**与内容同向：手指向左滑，时间向后推进（与地图类应用一致）
- **视窗状态跨页面保持**：从时间轴点进事件详情再返回，仍停在离开前的位置与缩放级别
- **缩放范围**：每年 0.0008–400 像素，可从「一眼万年」放大到以天为单位观察单年事件
- **对照页跳转**：点「前500」这类年代按钮，中国史与世界史两侧列表各自动画滚动到包含该年的时期
- **年表树左列对齐**：脊柱高度按右侧实际布局精确计算（含子块与孙块分组之间的间距）
- **搜索框收起**：时间轴 / 人物志 / 事件流的搜索默认隐藏，点右上角放大镜展开，不占首屏
- **编年主干判定**以数据里的 `编年主干` 标签为准，不靠区间重叠推断——史实本身存在合理重叠（隋唐 581 起而三国两晋南北朝到 589 止、宋辽金 916 起而五代十国到 979 止），用重叠判据会把朝代误藏起来

---

## 工程结构

```
history-atlas/
  app/src/main/
    java/com/historyatlas/app/
      MainActivity.kt              单 Activity 入口 + 后台预解析数据
      data/
        Models.kt                  数据契约模型（kotlinx-serialization）
        HistoryRepository.kt       assets 读取 / 索引 / 引用容错 / 搜索 / 主干拆分
      ui/
        AppNavHost.kt              Compose Navigation 路由（scope 经 query 传递）
        MainViewModel.kt           中国史 / 世界史分支切换
        components/
          CommonComponents.kt      徽章 / 星级 / 头像 / 引用卡 / 高亮文本 / 芯片
          PeriodBlock.kt           年表色块 + 时代脊柱 + 布局算法
          TimelineAxis.kt          横向缩放时间轴（Canvas 绘制）
        screens/                   9 个页面
      ui/theme/                    马卡龙配色 + 23 个 colorKey 映射
    assets/data/                   china.json / world.json（由脚本注入）
    res/                           自适应图标（青玉底 + 「史」字）+ 主题

data/
  SCHEMA.md                        ★ 数据契约（内容与代码的唯一依据）
  china.json                       中国史内容
  world.json                       世界史内容

docs/
  UI_SPEC.md                       界面与交互规格
  DESIGN.md                        产品与技术设计文档（8.6 万字）

tools/
  build_data.py                    ★ 数据流水线总入口（合并 → 修复 → 校验）
  fix_pipeline.py                  修复流水线（年份归一 / 引用补齐 / 中文化 / 详情补全）
  merge_shards.py                  分片合并 + 键名归一 + 日期补全 + 英文残留清理
  validate_data.py                 数据校验器（引用完整性 / 枚举 / 年份合法性 / 分类聚合）
  auto_fill_dangling.py            悬空引用自动补齐（事件 / 人物）
  backfill_missing.py              中国史核心事件与人物的补充内容
  copy_cn_to_world.py              中国史真实人物内容借用到世界史
  apply_event_details.py           核心事件的逐条手写详述
  fill_event_detail.py             其余事件的模板化详情生成
  name_events.py / name_placeholders.py / translate_names.py
                                  事件名与人物名的中文化
  normalize_roles.py               人物 role 字段规范化（合并同义写法）
  reassign_periods.py / reassign_figures.py
                                  事件与人物按年份重新归位到正确时期
  polish_text.py / clean_mixed_text.py
                                  重复词与中英夹杂清理
  check_shard.py                   分片 JSON 体检（解析 / 必填字段 / 年份顺序）
  analyze_data.py                  覆盖度分析（时期树 / 世纪分布 / 类别占比）
  audit_text.py / audit_names.py   残留拉丁字母检查
  ui_drive.py / capture_screens.py
                                  UI 自动化（uiautomator 定位 + 点击 + 截图）

scripts/
  sync_data.ps1                    数据 → assets 同步（带四项校验）
```

---

## 数据契约

三个实体，单向引用：

```
periods[].parentId      → periods[].id
periods[].keyFigures    → figures[].id
periods[].relatedEvents → events[].id
events[].periodId       → periods[].id
events[].figures        → figures[].id
figures[].periodId      → periods[].id
figures[].relatedEvents → events[].id
figures[].relatedFigures→ figures[].id
```

约定：
- **年份负数表示公元前**（前221 = `-221`），不使用 0 年
- 每个数值年份字段都配一个展示字段（`startYear` / `startDateText`）
- `category` 与 `colorKey` 使用固定枚举（见 `data/SCHEMA.md` §5、§6）
- 悬空引用由 `HistoryRepository` 在索引阶段剔除，不会在 UI 崩溃

### 数据流水线

`tools/build_data.py` 是数据进入 App 的唯一入口。它分三段：

**① 合并**（`merge_shards.py`）
- 键名归一 —— 同时接受缩写键（`id/n/y/ye/p/c/loc/imp/s/d/f/t`）与完整键
- 日期补全 —— 数据方只给数值年份时，自动生成 `dateText` / `startDateText` / `lifeText`
- 年份符号校正 —— 以 `lifeText` / `dateText` 为准修正 `by`/`dy`/`year`/`yearEnd` 的正负号
- 英文残留清理 —— 删除生成过程中混入的英文单词（只删不译，避免造出病句）

**② 修复**（`fix_pipeline.py`，十四个步骤按序执行）

| 步骤 | 作用 |
|---|---|
| `fix_year_order` / `fix_year_signs` / `fix_event_years` | 年份顺序与符号归一（负数=公元前，数值小=更早） |
| `backfill_missing` | 补齐中国史核心事件与人物 |
| `auto_fill_dangling` | 扫描全部悬空引用并补齐条目 |
| `add_missing_periods` | 补齐缺失的时期节点（如西夏、蒙古帝国） |
| `reassign_periods` / `reassign_figures` | 按事件年份与人物生卒年重新归位 |
| `fix_malformed_ids` | 规范化畸形 id（带空格/大写）并同步所有引用 |
| `merge_duplicate_figures` | 合并同一人物的重复条目，取内容最丰富的版本并合并关联 |
| `prune_fabricated` | 删除音译推测出来、无考据依据的占位人物及其引用 |
| `name_events` / `translate_names` / `name_placeholders` | 事件名与人物名的中文化 |
| `apply_event_details` / `fill_event_detail` | 核心事件用手写详述，其余用按类别区分的模板 |
| `clean_mixed_text` / `polish_text` / `normalize_roles` | 中英夹杂与重复词清理、role 规范化 |
| `fit_text_length` | 把 summary 收进长度区间，只用已有字段补足 |

世界史在修复前会额外执行 `copy_cn_to_world.py`，把中国史的真实人物内容借用到世界史中同 id 的条目上。

**③ 校验**（`validate_data.py`）

覆盖引用完整性、id 唯一性、枚举合法性、年份顺序、文本长度，并可按错误类型聚合输出：

```powershell
python tools\validate_data.py --summary data\china.json data\world.json
```

当前状态：**中国史与世界史均为 ERROR = 0**。

### 内容校验

```powershell
python tools\validate_data.py data\china.json data\world.json
python tools\analyze_data.py data\china.json
```

---

## 技术选型

| 项 | 选择 | 理由 |
|---|---|---|
| UI | Jetpack Compose + Material3 | 声明式，自定义绘制与手势支持好 |
| 架构 | 单 Activity + Navigation Compose | 无 DI 框架依赖，编译快、依赖少 |
| 数据 | assets JSON + kotlinx-serialization | 纯离线，无数据库；序列化比反射式解析快 |
| 依赖策略 | 最小依赖集，无 Hilt/KSP/Room/Retrofit | 降低构建风险，APK 体积小 |
| 权限 | **无网络权限** | 纯离线内容型 App |
| 最低版本 | minSdk 26（Android 8.0） | 覆盖 95%+ 设备 |
| 目标版本 | targetSdk 35 | |

**版本组合**：Gradle 8.14.2 ｜ AGP 8.11.1 ｜ Kotlin 2.1.21 ｜ Compose BOM 2024.10.01 ｜ kotlinx-serialization-json 1.7.3

---

## 后续路线

- **V1.1**：Room 本地库 + 离线热更新、收藏与笔记、横向年表视图
- **V1.2**：学习模式 —— 题库生成、答题闯关、错题本
- **V2.0**：自定义双文明对比、地图视图、事件因果图谱、跨设备同步

详见 `docs/DESIGN.md`。
