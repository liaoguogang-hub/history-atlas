# 科学图鉴 App 数据契约 v1

> 本文件是**内容生产者（数据生成）**与**App 开发者（代码）**之间的唯一契约。
> 字段名、类型、取值范围一经确定不得随意更改；如需扩展请升版本号并在文末记录变更。

本契约与 `history-atlas` 的历史图鉴契约同构，但把「朝代 / 历史事件 / 人物」
三组实体映射为自然科学语境下的「**分期 / 发现事件 / 科学家**」。

---

## 1. 顶层结构

每个数据文件是**一个 JSON 对象**，顶层只有 4 个字段：

```json
{
  "version": 1,
  "scope": "geo",
  "periods": [ ... ],
  "events":  [ ... ],
  "figures": [ ... ]
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `version` | int | 契约版本，当前固定 `1` |
| `scope` | string | `"geo"` / `"astro"` / `"physics"` / `"chem"`，决定文件归属与默认 UI 文案 |
| `periods` | array | 分期节点，构成主年表树 |
| `events` | array | 学科事件，挂在分期下 |
| `figures` | array | 科学家，挂在分期下 |

**四个 scope 的约定**

| scope | 学科 | 对应数据文件 |
|---|---|---|
| `geo` | 地理 | `data-science/geo.json` |
| `astro` | 天文学 | `data-science/astro.json` |
| `physics` | 物理学 | `data-science/physics.json` |
| `chem` | 化学 | `data-science/chem.json` |

**三个数组通过 `id` 互相引用（单向引用，避免循环结构）：**

- `period.parentId` → 上级分期的 `id`（顶层为 `null`）
- `event.periodId` → 所属分期的 `id`（必须存在）
- `figure.periodId` → 所属分期的 `id`（必须存在）
- `event.figures[]` / `period.relatedEvents[]` → 引用的 `event.id`（可为空数组）
- `figure.relatedEvents[]` / `figure.relatedFigures[]` → 引用的 `id`（可为空数组）

> **允许悬空引用**：App 必须对不存在的 id 做容错（跳过而非崩溃）。

---

## 2. `periods[]` — 分期节点

在自然科学语境下，`period` 表示一个**分期 / 理论体系 / 尺度层级**
（例如「板块构造学说时代」「量子力学时代」「地质年代·古生代」）。

```json
{
  "id": "geo-plate-tectonics",
  "name": "板块构造学说",
  "alias": "大陆漂移与海岭扩张",
  "parentId": "geo-modern",
  "startYear": 1912,
  "endYear": 1968,
  "startDateText": "公元1912年",
  "endDateText": "公元1968年",
  "colorKey": "geo-deep",
  "summary": "……",
  "territory": "全球",
  "capital": "伦敦、剑桥",
  "population": "数百名研究者",
  "culture": "地幔对流、海岭扩张与俯冲带",
  "keyFigures": ["fig-geo-wegener"],
  "relatedEvents": ["ev-geo-wegener-drift"],
  "tags": ["编年主干", "板块"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII，小写中划线。地理 `geo-`、天文 `astro-`、物理 `phy-`、化学 `chem-` 前缀 |
| `name` | string | ✅ | 分期主名 |
| `alias` | string | ❌ | 别名 / 全称 |
| `parentId` | string \| null | ✅ | 上级分期 id，顶层为 `null` |
| `startYear` | int | ✅ | 起始年，**负数表示公元前** |
| `endYear` | int | ✅ | 结束年（公元前 = 负数）。至今仍延续的用 `2026` |
| `startDateText` | string | ✅ | 展示用，如 `公元前400年` / `公元1912年` / `46亿年前` |
| `endDateText` | string | ✅ | 展示用 |
| `colorKey` | string | ❌ | 配色键，见 §6 |
| `summary` | string | ✅ | 分期概述，150–400 字 |
| `territory` | string | ❌ | 地理=分布范围；天文=观测波段/适用尺度；物理=适用领域；化学=研究对象 |
| `capital` | string | ❌ | 地理=代表地名；天文=代表观测站/探测器；物理=代表机构/学派中心；化学=代表实验室 |
| `population` | string | ❌ | 地理=面积/人口；天文=样本规模；物理=研究者规模；化学=已知化合物数量级 |
| `culture` | string | ❌ | 地理=地貌/气候特征；天文=核心理论/观测技术；物理=核心概念与范式；化学=核心概念与代表理论 |
| `keyFigures` | string[] | ❌ | 关键科学家 figure id |
| `relatedEvents` | string[] | ❌ | 代表性事件 id |
| `tags` | string[] | ❌ | 检索标签 |

**分期树规则**
- `startYear` 必须 ≤ `endYear`
- 子节点的年份区间必须**完全落在**父节点区间内（允许边界重合）
- 建议深度 ≤ 3 层（顶层分期 → 子分期 → 细分）
- 顶层分期本身就是可点击的条目，**不要**把所有内容都塞进一个根节点
- **顶层分期的 `tags` 里应含 `编年主干`**，它会强制该分期进入主干分组

> **关于「编年主干」标签**：学科史里存在合理的时间重叠（经典力学与热学在 19 世纪交叠）。
> 仅靠区间重叠判断主干会把这些主线分期误判成专题并藏起来。带 `编年主干` 标签的
> 分期**无条件**进入主干。

> **关于「专题」标签**：`tags` 含 `专题` / `跨尺度` / `区域专题`，
> 或 `colorKey = "purple"` 的分期，直接归入「专题补充」组，单独成组展示。

---

## 3. `events[]` — 学科事件

在自然科学语境下，`event` 表示一次**发现 / 理论提出 / 技术突破 / 重大观测**。

```json
{
  "id": "ev-geo-wegener-drift",
  "name": "魏格纳提出大陆漂移学说",
  "year": 1912,
  "yearEnd": null,
  "dateText": "公元1912年",
  "periodId": "geo-plate-tectonics",
  "category": "scientific",
  "location": "法兰克福",
  "summary": "一句话摘要，40–120 字",
  "detail": "详细叙述，150–800 字",
  "importance": 5,
  "figures": ["fig-geo-wegener"],
  "tags": ["大陆漂移", "地质学"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII。前缀 `ev-geo-` / `ev-astro-` / `ev-phy-` / `ev-chem-` |
| `name` | string | ✅ | 事件名 |
| `year` | int | ✅ | 发生年，公元前为负 |
| `yearEnd` | int \| null | ❌ | 跨年事件的结束年（如持续观测、长期实验），单点事件为 `null` |
| `dateText` | string | ✅ | 展示用精确日期 |
| `periodId` | string | ✅ | 所属分期 id |
| `category` | string | ✅ | 分类，见 §5 |
| `location` | string | ❌ | 发生地 / 观测地 |
| `summary` | string | ✅ | 一句话摘要，40–120 字 |
| `detail` | string | ✅ | 详细叙述，150–800 字 |
| `importance` | int | ✅ | 重要度 `1`–`5`，5 为改变学科走向 |
| `figures` | string[] | ❌ | 涉及科学家 id |
| `tags` | string[] | ❌ | 检索标签 |

> **时间轴关键**：事件跨度用于在时间轴上绘制色条。`yearEnd` 为 `null` 时跨度为 0（时间点）。

---

## 4. `figures[]` — 科学家

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII。前缀 `fig-geo-` / `fig-astro-` / `fig-phy-` / `fig-chem-` |
| `name` | string | ✅ | 姓名 |
| `alias` | string | ❌ | 字/号/别名，`、` 分隔 |
| `birthYear` | int \| null | ❌ | 生年，公元前为负；不详为 `null` |
| `deathYear` | int \| null | ❌ | 卒年，公元前为负；不详为 `null` |
| `lifeText` | string | ✅ | 展示用生卒，如 `1880年－1930年` |
| `role` | string | ✅ | 身份，如 `地质学家`、`天文学家`、`理论物理学家`、`化学家` |
| `periodId` | string | ✅ | 所属分期 id |
| `gender` | string | ❌ | `"male"` / `"female"` / `"unknown"` |
| `summary` | string | ✅ | 一句话简介，40–120 字 |
| `biography` | string | ✅ | 生平详述，200–1000 字 |
| `achievements` | string[] | ❌ | 主要成就，3–6 条 |
| `quotes` | string[] | ❌ | 名言/史料引文，0–3 条 |
| `relatedEvents` | string[] | ❌ | 相关事件 id |
| `relatedFigures` | string[] | ❌ | 相关人物 id |
| `tags` | string[] | ❌ | 检索标签 |

---

## 5. `category` 事件分类枚举

必须使用以下固定值之一，App 依此显示图标与配色：

| 值 | 中文 | 值 | 中文 |
|---|---|---|---|
| `scientific` | 科学发现 | `military` | 军事 |
| `technology` | 技术 | `economic` | 经济 |
| `exploration` | 探索/观测 | `cultural` | 文化 |
| `reform` | 理论变革 | `social` | 社会 |
| `education` | 教育 | `religious` | 宗教 |
| `art` | 艺术 | `literature` | 文学 |
| `political` | 政治 | `treaty` | 条约/协作 |
| `conflict` | 冲突 | `dynasty` | 奠基/更替 |
| `cross-civilization` | 跨学科交流 | `disaster` | 灾难/事故 |
| `health` | 医学/健康 | `economy-crisis` | 危机 |
| `legend` | 传说/假说 | `archaeology` | 考古/遗址 |

> **自然科学内容的主用分类**：`scientific`（发现与理论）、`technology`（仪器与工业应用）、
> `exploration`（观测、考察、远征）、`reform`（理论范式变革）、
> `cross-civilization`（跨学科交流）、`disaster`（事故）、`treaty`（国际协作）。

---

## 6. `colorKey` 配色键

每个学科有自己的色系。App 侧的定义见 `app/src/main/java/com/scienceatlas/app/ui/theme/ColorKeys.kt`，
未列出的键会走哈希回退调色板（仍能得到稳定柔和的配色）。

### 地理（`geo-`）

| 键 | 含义 | 键 | 含义 |
|---|---|---|---|
| `geo-deep` | 地质深时 | `geo-river` | 河流水系 |
| `geo-coast` | 海岸地貌 | `geo-ocean` | 海洋 |
| `geo-plain` | 平原 | `geo-volcano` | 火山 |
| `geo-mountain` | 山地 | `geo-karst` | 喀斯特 |
| `geo-desert` | 荒漠 | `geo-polar` | 冰冻圈 |

### 天文（`astro-`）

| 键 | 含义 | 键 | 含义 |
|---|---|---|---|
| `astro-deep` | 深空观测 | `astro-galaxy` | 星系 |
| `astro-solar` | 太阳系 | `astro-telescope` | 观测技术 |
| `astro-planet` | 行星 | `astro-quanta` | 量子与辐射 |
| `astro-comet` | 小天体 | `astro-cosmo` | 宇宙学 |

### 物理（`phy-`）

| 键 | 含义 | 键 | 含义 |
|---|---|---|---|
| `phy-classical` | 经典力学 | `phy-particle` | 粒子物理 |
| `phy-thermo` | 热学 | `phy-relativity` | 相对论 |
| `phy-em` | 电磁学 | `phy-wave` | 波动与声学 |
| `phy-quantum` | 量子力学 | `phy-astro` | 理论物理 |
| `phy-nuclear` | 核物理 | `phy-condensed` | 凝聚态 |

### 化学（`chem-`）

| 键 | 含义 | 键 | 含义 |
|---|---|---|---|
| `chem-alchemy` | 炼金与早期化学 | `chem-structure` | 结构化学 |
| `chem-atomic` | 原子论 | `chem-bio` | 生物化学 |
| `chem-periodic` | 周期律 | `chem-nuclear` | 核化学 |
| `chem-organic` | 有机化学 | `chem-material` | 材料化学 |
| `chem-electro` | 电化学 | `chem-industry` | 工业化学 |

### 通用

| 键 | 含义 |
|---|---|
| `purple` | 跨尺度 / 专题（强制归入「专题补充」组） |

---

## 7. 校验清单

生成数据后必须逐项通过：

- [ ] 每个文件顶层恰有 `version` / `scope` / `periods` / `events` / `figures`
- [ ] `scope` 与文件名一致
- [ ] 所有 `id` 在各自数组内唯一，且跨文件不冲突
- [ ] 所有 `parentId` / `periodId` 指向真实存在的 id
- [ ] `keyFigures` / `relatedEvents` / `relatedFigures` / `figures` 引用均存在
- [ ] 每个 `period` 满足 `startYear ≤ endYear`
- [ ] 子分期的年份区间落在父分期内
- [ ] 分期树深度 ≤ 3
- [ ] 每个事件的 `category` 是 §5 的合法枚举值
- [ ] 每个 `importance` 在 1..5 之间
- [ ] 顶层分期的 `tags` 含 `编年主干`

仓库中的校验脚本：`tools/sci_content/validate_sci.py`。

---

## 8. 变更记录

| 版本 | 变更 |
|---|---|
| 1 | 初版。由 `history-atlas` 的历史图鉴契约改造而来，实体语义从「朝代/事件/人物」映射为「分期/发现/科学家」，并新增四学科配色键。 |
