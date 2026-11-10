# 历史图鉴 App 数据契约 v1

> 本文件是**内容生产者（数据生成）**与**App 开发者（代码）**之间的唯一契约。
> 字段名、类型、取值范围一经确定不得随意更改；如需扩展请升版本号并在文末记录变更。

## 1. 顶层结构

每个数据文件是**一个 JSON 对象**，顶层只有 4 个字段：

```json
{
  "version": 1,
  "scope": "china",
  "periods": [ ... ],
  "events":  [ ... ],
  "figures": [ ... ]
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `version` | int | 契约版本，当前固定 `1` |
| `scope` | string | `"china"` 或 `"world"`，决定文件归属与默认 UI 文案 |
| `periods` | array | 时期（朝代）节点，构成主年表树 |
| `events` | array | 历史事件，挂在时期下 |
| `figures` | array | 人物，挂在时期下 |

**三个数组通过 `id` 互相引用（单向引用，避免循环结构）：**

- `period.parentId` → 上级时期的 `id`（顶层为 `null`）
- `event.periodId` → 所属时期的 `id`（必须存在）
- `figure.periodId` → 所属时期的 `id`（必须存在）
- `event.figures[]` / `period.relatedEvents[]` → 引用的 `event.id`（可为空数组）
- `figure.relatedEvents[]` / `figure.relatedFigures[]` → 引用的 `id`（可为空数组）

> **允许悬空引用**：App 必须对不存在的 id 做容错（跳过而非崩溃）。

---

## 2. `periods[]` — 时期节点

```json
{
  "id": "cn-qin",
  "name": "秦",
  "alias": "秦朝",
  "parentId": "cn-empire",
  "startYear": -221,
  "endYear": -207,
  "startDateText": "公元前221年",
  "endDateText": "公元前207年",
  "colorKey": "qin",
  "summary": "中国第一个统一的中央集权王朝……",
  "territory": "东至东海，西至陇西，北至长城一带，南至南海",
  "capital": "咸阳",
  "population": "约2000万",
  "culture": "秦篆、秦隶；律法严明；统一度量衡与文字",
  "keyFigures": ["fig-li-si", "fig-zi-ying", "fig-zhao-gao"],
  "relatedEvents": ["ev-qin-unify", "ev-qin-territ"],
  "tags": ["统一", "中央集权"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII，小写中划线，如 `cn-han` |
| `name` | string | ✅ | 时期主名，如 `西汉` |
| `alias` | string | ❌ | 别名/全称，如 `西汉` |
| `parentId` | string \| null | ✅ | 上级时期 id，顶层为 `null` |
| `startYear` | int | ✅ | 起始年，**负数表示公元前**（公元前221 = `-221`） |
| `endYear` | int | ✅ | 结束年（公元前 = 负数）。至今仍延续的用 `2026` |
| `startDateText` | string | ✅ | 展示用，如 `公元前221年` |
| `endDateText` | string | ✅ | 展示用，如 `公元前207年` |
| `colorKey` | string | ❌ | 配色键，见 §6 |
| `summary` | string | ✅ | 时期概述，150–400 字 |
| `territory` | string | ❌ | 疆域范围描述 |
| `capital` | string | ❌ | 都城，可多个用 `、` 分隔 |
| `population` | string | ❌ | 人口估计，字符串以免歧义 |
| `culture` | string | ❌ | 文化/制度/社会风貌 |
| `keyFigures` | string[] | ❌ | 关键人物 figure id |
| `relatedEvents` | string[] | ❌ | 代表性事件 id |
| `tags` | string[] | ❌ | 检索标签 |

**时期树规则**
- `startYear` 必须 ≤ `endYear`
- 子节点的年份区间必须**完全落在**父节点区间内（允许边界重合）
- 建议深度 ≤ 3 层（顶层朝代 → 次级政权 → 细分）
- 顶层朝代（如 `cn-han`）本身就是可点击的时期，**不要**把所有内容都塞进一个根节点

---

## 3. `events[]` — 历史事件

```json
{
  "id": "ev-qin-unify",
  "name": "秦灭六国完成统一",
  "year": -221,
  "yearEnd": null,
  "dateText": "公元前221年",
  "periodId": "cn-qin",
  "category": "political",
  "location": "咸阳",
  "summary": "秦王政先后灭韩赵魏楚燕齐，结束战国五百年分裂，建立统一王朝。",
  "detail": "公元前230年秦灭韩……（150–800 字，叙述史实，可含纪年细节）",
  "importance": 5,
  "figures": ["fig-qin-shi-huang"],
  "tags": ["统一", "战争"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII，如 `ev-qin-unify` |
| `name` | string | ✅ | 事件名 |
| `year` | int | ✅ | 发生年，公元前为负 |
| `yearEnd` | int \| null | ❌ | 跨年事件的结束年（如战争、变法），单点事件为 `null` |
| `dateText` | string | ✅ | 展示用精确日期，如 `公元前221年` / `公元前221年10月` / `公元105年` |
| `periodId` | string | ✅ | 所属时期 id |
| `category` | string | ✅ | 分类，见 §5 |
| `location` | string | ❌ | 发生地 |
| `summary` | string | ✅ | 一句话摘要，40–120 字 |
| `detail` | string | ✅ | 详细叙述，150–800 字 |
| `importance` | int | ✅ | 重要度 `1`–`5`，5 为改变历史走向 |
| `figures` | string[] | ❌ | 涉及人物 id |
| `tags` | string[] | ❌ | 检索标签 |

> **时间轴关键**：事件跨度用于在时间轴上绘制色条。`yearEnd` 为 `null` 时跨度为 0（时间点）。

---

## 4. `figures[]` — 人物

```json
{
  "id": "fig-qin-shi-huang",
  "name": "秦始皇",
  "alias": "嬴政、始皇帝",
  "birthYear": -259,
  "deathYear": -210,
  "lifeText": "公元前259年－公元前210年",
  "role": "皇帝",
  "periodId": "cn-qin",
  "gender": "male",
  "summary": "秦王政即秦始皇，战国末期秦国君主，了中国第一个统一王朝。",
  "biography": "公元前246年十三岁即位……（200–1000 字）",
  "achievements": ["统一六国", "建立中央集权制度", "统一文字度量衡", "修筑长城与驰道"],
  "quotes": ["朕为始皇帝，后世以计数，二世三世至于万世，传之无穷。"],
  "relatedEvents": ["ev-qin-unify", "ev-qin-burn-books"],
  "relatedFigures": ["fig-li-si", "fig-han-gao-zu"],
  "tags": ["皇帝", "统一"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一，ASCII，如 `fig-qin-shi-huang` |
| `name` | string | ✅ | 姓名 |
| `alias` | string | ❌ | 字/号/别名，`、` 分隔 |
| `birthYear` | int \| null | ❌ | 生年，公元前为负；不详为 `null` |
| `deathYear` | int \| null | ❌ | 卒年，公元前为负；不详为 `null` |
| `lifeText` | string | ✅ | 展示用生卒，如 `公元前259年－公元前210年` |
| `role` | string | ✅ | 身份，如 `皇帝`、`政治家`、`科学家`、`诗人`、`将领` |
| `periodId` | string | ✅ | 所属时期 id |
| `gender` | string | ❌ | `"male"` / `"female"` / `"unknown"` |
| `summary` | string | ✅ | 一句话简介，40–120 字 |
| `biography` | string | ✅ | 生平详述，200–1000 字 |
| `achievements` | string[] | ❌ | 主要成就，3–6 条 |
| `quotes` | string[] | ❌ | 名言/史料引文，0–3 条 |
| `relatedEvents` | string[] | ❌ | 相关事件 id |
| `relatedFigures` | string[] | ❌ | 相关人物 id（关联他人） |
| `tags` | string[] | ❌ | 检索标签 |

---

## 5. `category` 事件分类枚举

必须使用以下固定值之一，App 依此显示图标与配色：

| 值 | 中文 | 值 | 中文 |
|---|---|---|---|
| `political` | 政治 | `military` | 军事 |
| `economic` | 经济 | `cultural` | 文化 |
| `scientific` | 科技 | `social` | 社会 |
| `religious` | 宗教 | `art` | 艺术 |
| `literature` | 文学 | `education` | 教育 |
| `technology` | 技术 | `exploration` | 探索/地理 |
| `conflict` | 战争/冲突 | `treaty` | 条约/外交 |
| `reform` | 改革/变法 | `dynasty` | 王朝更替/建国 |
| `cross-civilization` | 跨文明交流 | `disaster` | 灾难/灾荒 |
| `health` | 医学/疾病 | `economy-crisis` | 经济危机 |
| `legend` | 传说/神话 | `archaeology` | 考古/遗址 |

> 跨文明关联（世界史专用）：如「丝绸之路开通」「蒙古西征」这类同时影响多个文明的事件，
> `category` 用 `cross-civilization`，`location` 写路径，`tags` 标注相关文明名（如 `["罗马", "汉朝", "波斯"]`）。

---

## 6. `colorKey` 配色键

App 内置一套淡雅分块配色（接近参考图的柔和马卡龙色系）。时期节点通过 `colorKey` 指定色块，
未指定时由 App 按 `id` 哈希自动分配。

**中国史推荐键**（对应参考图配色）：

```
stone    石器/远古    cyan     夏商
zhou     西周/东周    blue     秦
han      汉            green    三国两晋南北朝
sui-tang 隋唐         yellow   五代宋辽金
yuan     元            pink     明
qing     清            gray     民国/近代
modern   现代          purple   跨朝代/专题
```

**世界史推荐键**：

```
prehistory  史前      mesopotamia  两河/埃及
india       印度河    greece       古希腊
rome        古罗马    medieval     中世纪
renaissance  文艺复兴  earlymodern  近代早期
modern      近代      contemporary 当代
```

任意 `colorKey` 字符串都可用，App 有 fallback。

---

## 7. 书写规范

1. **正负年份**：`startYear`/`year`/`birthYear` 等所有数值年份，公元前一律为负数，公元后为正数（无 `0` 年问题，不使用 0）。
2. **展示文本与数值并存**：`dateText` / `lifeText` 用于 UI 展示（含「公元前」字样），数值字段用于计算排序与时间轴定位。两者必须一致。
3. **未知信息**用 `null` 或省略，不要编造具体数字（如人口估计用 `约3000万` 而非精确值）。
4. **史实优先**：有争议的史实用「一说」「一般认为」等表述，不下绝对结论。
5. **文字长度**：`summary` 40–120 字；`detail` 150–800 字；`biography` 200–1000 字。
6. **id 命名**：`cn-`/`world-` 前缀区分归属，`ev-` 事件，`fig-` 人物，全小写中划线。

---

## 8. 校验规则（数据必须通过）

- ✅ 顶层 JSON 可解析，`version`/`scope`/`periods`/`events`/`figures` 均存在
- ✅ 所有 id 全局唯一
- ✅ 所有 `periodId` / `parentId` 指向存在的时期（允许悬空，但不允许指向自身）
- ✅ 所有 `colorKey` 属于 §6 枚举或为未知 fallback
- ✅ 所有 `category` 属于 §5 枚举
- ✅ 所有 `importance` ∈ {1,2,3,4,5}
- ✅ 所有年份满足 `startYear ≤ endYear`、`birthYear ≤ deathYear`
- ✅ 事件 `periodId` 所属时期的区间包含该事件的年份
- ✅ JSON 文件为 UTF-8 无 BOM

校验脚本：`tools/validate_data.py`

---

## 9. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1 | 2026-11-10 | 初版，定义 periods / events / figures 三实体及其引用关系 |
