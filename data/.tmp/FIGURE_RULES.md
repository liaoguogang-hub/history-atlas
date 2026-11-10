# 人物 periodId 权威映射

## 背景与结论

`missing_figure_ids.json` 里的 periodId 是**从时期树反推**的，粒度不总准确 ——
例如把「房玄龄」（唐初宰相）分到了 `cn-nanbei-south`（南朝），
把「李建成」（唐太子）分到了 `cn-wudai-south`（十国）。

**结论：以人物实际生平为准。** 本文件 `figure_period_map.json` 是权威映射。

## 使用方法

写任何人物分片时，`p` 字段的取值规则：

1. 如果 `figure_period_map.json` 里有这个 id → **直接用映射里的值**
2. 如果没有 → 按下列原则判断：
   - 优先挂到**人物生平所属的最具体时期**
   - 顶层大时期（如 `cn-tang`）只在其下没有更合适的子时期时使用
   - 拿不准时挂到该人物主要活动的那个顶层时期

## 已确认的历史时期层级（写数据时对照）

```
cn-prehistory      远古石器          cn-pre-paleolithic  旧石器时代
cn-xia-shang      夏商              cn-xia / cn-shang
cn-zhou-west      西周              cn-zhou-east        东周
                                     cn-spring-autumn    春秋
                                     cn-warring-states   战国
cn-han             汉                cn-han-west         西汉
                                     cn-han-east         东汉
                                     cn-wangmang         新莽
cn-wei-jin-nanbei 三国两晋南北朝     cn-three-kingdoms   三国
                                     cn-three-shu        蜀汉
                                     cn-three-wei        曹魏
                                     cn-three-wu         东吴
                                     cn-liang-jin        两晋
                                     cn-sixteen-kingdoms 十六国
                                     cn-nanbei           南北朝
                                     cn-nanbei-north     北朝
                                     cn-nanbei-south     南朝
cn-sui-tang       隋唐              cn-sui / cn-tang
                                     cn-tang-early      唐初（高祖武德至开元前）
                                     cn-tang-mid        唐中期（开天至安史乱前）
                                     cn-tang-late       唐后期（安史乱至亡）
cn-wudai           五代十国           cn-wudai-north      五代
                                     cn-wudai-south      十国
cn-song-liao-jin   宋辽金             cn-song            两宋
                                     cn-song-north      北宋
                                     cn-song-south      南宋
                                     cn-liao / cn-jin / cn-xixia
cn-yuan            元                cn-yuan-early      元初（窝阔台至忽必烈前期）
                                     cn-yuan-late       元后期
cn-ming            明                cn-ming-early / cn-ming-mid / cn-ming-late
cn-qing            清                cn-qing-early / cn-qing-mid / cn-qing-late
cn-modern          近代               cn-modern-republic     民国
                                     cn-modern-anti-japan   抗日战争
                                     cn-modern-liberation   解放战争
cn-prc             中华人民共和国      cn-prc-early       1949—1978
                                     cn-prc-reform      1978—2012
                                     cn-prc-new-era     2012—
```

## 关键人物的正确归属（最容易搞错的）

| 人物 | 正确 periodId | 常见错误 |
|---|---|---|
| 曹操 | cn-han-east | — |
| 曹丕 / 曹叡 / 曹植 / 曹爽 | cn-three-wei | cn-han-east |
| 刘备 / 诸葛亮 / 关羽 / 张飞 / 赵云 / 刘禅 | cn-three-shu | cn-three-kingdoms |
| 孙权 / 周瑜 / 吕蒙 / 陆逊 / 太史慈 / 王濬 / 孙皓 | cn-three-wu | cn-three-kingdoms |
| 司马懿 | cn-han-east | cn-three-wei |
| 司马师 / 司马昭 | cn-three-wei | — |
| 司马睿（晋元帝）/ 谢安 / 谢玄 | cn-liang-jin | cn-wei-jin-nanbei |
| 陶渊明 / 王羲之 | cn-jin-east | cn-liang-jin |
| 刘裕 / 萧衍 / 陈霸先 / 侯景 | cn-nanbei-south | cn-nanbei |
| 拓跋珪 / 孝文帝 / 冯太后 / 宇文泰 / 高欢 / 杨坚 | cn-nanbei-north | cn-nanbei |
| 李渊 / 李世民 / 房玄龄 / 杜如晦 / 魏征 / 武则天 / 狄仁杰 | cn-tang-early | cn-tang |
| 李白 / 杜甫 / 白居易 / 韩愈 / 刘禹锡 / 郭子仪 / 李光弼 / 安禄山 | cn-tang-mid | cn-tang-early |
| 房玄龄 | cn-tang-early | cn-nanbei-south |
| 李建成 | cn-tang-early | cn-wudai-south |
| 祖冲之 | cn-nanbei-south | — |
| 石勒 / 刘渊 / 苻坚 | cn-sixteen-kingdoms | cn-liang-jin |

## 事件引用（`re`）规则

`re` 里的事件 id 只能是这些前缀（其余一律清空该条目的 `re`）：

```
ev-pre-*   ev-xia-*   ev-shang-*   ev-zhou-*   ev-qin-*
ev-han-*   ev-weijin-*   ev-suita-*   ev-tang-*
```

注意：`ev-three-*` `ev-jin-*` `ev-nanbei-*` `ev-wudai-*` `ev-song-*` `ev-ming-*`
`ev-qing-*` `ev-yuan-*` `ev-modern-*` `ev-prc-*` 都不是合法事件 id 前缀。

## 人物引用（`rf`）规则

`rf` 里的 id 必须在「现有 figures ∪ missing_figure_ids.json ∪ figure_period_map.json」并集内，
越界的**逐条移除**（不是清空整个数组）。

## JSON 硬性约束

1. 字符串值内部**绝对不能出现半角双引号 `"`** —— 会提前结束 JSON 字符串。名言用「」或『』。
2. **不能出现裸控制字符**。每条记录写在一行内。
3. `by`/`dy` 不详用 JSON `null`，**不能写 `?`**（非法 JSON 值）。
   校验脚本 `tools/check_shard.py` 会自动把 `"by":-?` 修成 `"by":null`。
4. 年份负数表示公元前，数值越小越早，因此 `by <= dy` 为正常。

## 自检命令

```
cd C:\Users\guoga\Documents\DSH
python tools\check_shard.py data\.tmp\figdata_fillX.json
```

必须输出 `PARSE OK` 且 `records missing required fields: 0`。

合并与校验：
```
python tools\merge_shards.py --scope china --out data\china.json "data\.tmp\china_periods.json" "data\.tmp\evdata_*.json" "data\.tmp\figdata_*.json"
python tools\validate_data.py data\china.json
```
