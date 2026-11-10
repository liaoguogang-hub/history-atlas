"""为「年份恰好等于时期起始年」的事件补上真实年份。

这些事件大多在自动补引用时被填成了所属时期的起始年，导致：
- 时间轴上同一时期的事件标记全部叠在一个点上
- 事件流里同年事件扎堆，看不出先后

表里只列**确实晚于时期起始年**的事件；王朝建立类事件本来就发生在
时期起始年，不需要改动。
"""
import io
import json
import sys

# id -> (真实年份, 说明)
YEAR_FIX = {
    # 夏：禹建夏朝在起始年，其后诸事各有其年
    "ev-xia-cheng": (-2050, "启继位后与有扈氏战于甘"),
    "ev-xia-taikang": (-2010, "太康失国，后羿代夏"),
    "ev-xia-zhongxing": (-1900, "少康中兴复国"),
    # 早商
    "ev-shang-yiyin": (-1590, "伊尹辅政"),
    "ev-shang-taijia": (-1580, "太甲放于桐宫"),
    "ev-shang-zhengzhou-city": (-1550, "郑州商城与偃师商城的使用期"),
    # 晚商
    "ev-shang-pan-geng": (-1295, "盘庚迁殷后整顿内政"),
    "ev-shang-jiagu": (-1250, "武丁时期甲骨占卜大盛"),
    "ev-shang-bronze": (-1220, "商代晚期青铜铸造巅峰"),
    # 西周
    "ev-zhou-fengjian": (-1040, "周公东征后的大分封"),
    # 汉
    "ev-han-wangtian": (10, "王莽推行王田私属制"),
    # 三国
    "ev-weijin-three-kingdoms": (229, "孙权称帝，三国鼎立最终形成"),
    # 南北朝
    "ev-weijin-northern-wei": (439, "北魏统一黄河流域"),
    # 隋
    "ev-suita-kaihuang": (590, "开皇之治的全盛期"),
    # 唐
    "ev-tang-poetry": (700, "唐诗黄金时代"),
    # 五代十国
    "ev-wudai-10guo": (907, "五代十国格局形成于唐亡之年"),
    # 宋
    "ev-song-xining": (1038, "元昊称帝建西夏"),
    # 元
    "ev-yuan-kublai": (1271, "忽必烈定国号大元"),
    # 新中国
    "ev-prc-belt-road": (2013, "一带一路倡议提出"),
    "ev-prc-poverty": (2021, "脱贫攻坚战取得全面胜利"),
    "ev-prc-carbon": (2020, "碳达峰碳中和目标提出"),
    "ev-prc-beidou": (2020, "北斗三号全球组网完成"),
    "ev-prc-tianwen": (2020, "天问一号发射"),
    "ev-prc-chang-e-five": (2020, "嫦娥五号月球采样返回"),
    "ev-prc-civilization": (2016, "文化自信与「两个结合」的提出"),
}

# 世界史：同样是「年份被填成时期起始年」中确实偏晚的条目
WORLD_YEAR_FIX = {
    "ev-byzantium-milan-edict": (313, "米兰敕令"),
    "ev-byzantium-nicaea": (325, "第一次尼西亚公会议"),
    "ev-byzantium-constantinople": (330, "君士坦丁堡建城"),
}


def fmt(y):
    return ("公元前%d年" % abs(y)) if y < 0 else ("公元%d年" % y)


def apply(path, table):
    d = json.load(io.open(path, encoding="utf-8"))
    by_id = {e["id"]: e for e in d.get("events") or []}
    n = 0
    for eid, (year, note) in table.items():
        e = by_id.get(eid)
        if e is None:
            continue
        if e.get("year") == year and e.get("dateText") == fmt(year):
            continue
        e["year"] = year
        e["dateText"] = fmt(year)
        n += 1
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{path}: 修正 {n} 个事件的年份")
    for eid, (year, note) in list(table.items())[:6]:
        print(f"   {eid} -> {fmt(year)}  ({note})")


if __name__ == "__main__":
    apply("data/china.json", YEAR_FIX)
    apply("data/world.json", WORLD_YEAR_FIX)
