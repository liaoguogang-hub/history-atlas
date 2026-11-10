package com.historyatlas.app.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 数据契约 v1 的顶层对象。
 *
 * 对应 `data/SCHEMA.md` §1：
 * ```json
 * { "version": 1, "scope": "china", "periods": [...], "events": [...], "figures": [...] }
 * ```
 *
 * 所有可选字段均带默认值，保证 assets 数据缺字段时不至于反序列化崩溃。
 */
@Serializable
data class HistoryDataset(
    val version: Int = 1,
    val scope: String = "",
    val periods: List<Period> = emptyList(),
    val events: List<Event> = emptyList(),
    val figures: List<Figure> = emptyList(),
)

/**
 * 时期（朝代）节点，契约 §2。
 *
 * - [parentId] 指向上级时期 id，顶层为 `null`。
 * - [startYear] / [endYear] 为负数表示公元前。
 */
@Serializable
data class Period(
    val id: String = "",
    val name: String = "",
    val alias: String = "",
    val parentId: String? = null,
    val startYear: Int = 0,
    val endYear: Int = 0,
    val startDateText: String = "",
    val endDateText: String = "",
    val colorKey: String = "",
    val summary: String = "",
    val territory: String = "",
    val capital: String = "",
    val population: String = "",
    val culture: String = "",
    val keyFigures: List<String> = emptyList(),
    val relatedEvents: List<String> = emptyList(),
    val tags: List<String> = emptyList(),
) {
    /** 所属时期的完整年份区间文本。 */
    val yearRangeText: String
        get() = when {
            startDateText.isNotEmpty() && endDateText.isNotEmpty() -> "$startDateText — $endDateText"
            startDateText.isNotEmpty() -> startDateText
            endDateText.isNotEmpty() -> endDateText
            else -> ""
        }
}

/**
 * 历史事件，契约 §3。
 *
 * [yearEnd] 为 `null` 表示时间点事件；[importance] 取值 1..5。
 */
@Serializable
data class Event(
    val id: String = "",
    val name: String = "",
    val year: Int = 0,
    val yearEnd: Int? = null,
    val dateText: String = "",
    val periodId: String = "",
    val category: String = "",
    val location: String = "",
    val summary: String = "",
    val detail: String = "",
    val importance: Int = 0,
    val figures: List<String> = emptyList(),
    val tags: List<String> = emptyList(),
) {
    /** 事件跨年跨度（`yearEnd` 为 null 时为 0）。 */
    val span: Int
        get() = (yearEnd ?: year) - year

    /** 时间轴色条绘制所需的起点/终点。 */
    val spanStart: Int get() = year
    val spanEnd: Int get() = yearEnd ?: year
}

/**
 * 人物，契约 §4。
 *
 * [birthYear] / [deathYear] 为 `null` 表示不详。
 */
@Serializable
data class Figure(
    val id: String = "",
    val name: String = "",
    val alias: String = "",
    val birthYear: Int? = null,
    val deathYear: Int? = null,
    val lifeText: String = "",
    val role: String = "",
    val periodId: String = "",
    val gender: String = "",
    val summary: String = "",
    val biography: String = "",
    val achievements: List<String> = emptyList(),
    val quotes: List<String> = emptyList(),
    val relatedEvents: List<String> = emptyList(),
    val relatedFigures: List<String> = emptyList(),
    val tags: List<String> = emptyList(),
)

/**
 * 事件分类枚举，契约 §5。
 *
 * 中文标签与配色键由 App 侧维护，数据文件只存英文枚举值。
 */
enum class EventCategory(val value: String, val label: String) {
    POLITICAL("political", "政治"),
    MILITARY("military", "军事"),
    ECONOMIC("economic", "经济"),
    CULTURAL("cultural", "文化"),
    SCIENTIFIC("scientific", "科技"),
    SOCIAL("social", "社会"),
    RELIGIOUS("religious", "宗教"),
    ART("art", "艺术"),
    LITERATURE("literature", "文学"),
    EDUCATION("education", "教育"),
    TECHNOLOGY("technology", "技术"),
    EXPLORATION("exploration", "探索/地理"),
    CONFLICT("conflict", "战争/冲突"),
    TREATY("treaty", "条约/外交"),
    REFORM("reform", "改革/变法"),
    DYNASTY("dynasty", "王朝更替/建国"),
    CROSS_CIVILIZATION("cross-civilization", "跨文明交流"),
    DISASTER("disaster", "灾难/灾荒"),
    HEALTH("health", "医学/疾病"),
    ECONOMY_CRISIS("economy-crisis", "经济危机"),
    LEGEND("legend", "传说/神话"),
    ARCHAEOLOGY("archaeology", "考古/遗址"),
    ;

    companion object {
        private val byValue = entries.associateBy { it.value }

        /** 未知分类回退到 [SOCIAL]，不会抛异常。 */
        fun from(value: String): EventCategory = byValue[value] ?: SOCIAL
    }
}

/**
 * 搜索结果聚合，跨时期 / 事件 / 人物三类实体匹配。
 */
data class SearchResult(
    val periods: List<Period> = emptyList(),
    val events: List<Event> = emptyList(),
    val figures: List<Figure> = emptyList(),
) {
    val isEmpty: Boolean get() = periods.isEmpty() && events.isEmpty() && figures.isEmpty()
    val total: Int get() = periods.size + events.size + figures.size
}
