package com.scienceatlas.app.data

import kotlinx.serialization.Serializable

/**
 * 数据契约 v1 的顶层对象。
 *
 * 对应 `data-science/SCHEMA.md` §1：
 * ```json
 * { "version": 1, "scope": "geo", "periods": [...], "events": [...], "figures": [...] }
 * ```
 *
 * 所有可选字段均带默认值，保证 assets 数据缺字段时不至于反序列化崩溃。
 */
@Serializable
data class ScienceDataset(
    val version: Int = 1,
    val scope: String = "",
    val periods: List<Period> = emptyList(),
    val events: List<Event> = emptyList(),
    val figures: List<Figure> = emptyList(),
)

/**
 * 分期节点，契约 §2。
 *
 * 在自然科学语境下，`period` 表示一个**分期 / 理论体系 / 尺度层级**
 * （例如「板块构造学说时代」「量子力学时代」「地质年代·古生代」）。
 *
 * - [parentId] 指向上级分期 id，顶层为 `null`。
 * - [startYear] / [endYear] 为负数表示公元前。
 *
 * **年份用 Long 而非 Int**：地质年代需要表达「约 46 亿年前」，
 * 即 -4600000000，超出 Int 的下限（-2147483648）。
 * 用 Int 会让整个数据文件反序列化失败，表现为「该学科内容全空」。
 */
@Serializable
data class Period(
    val id: String = "",
    val name: String = "",
    val alias: String = "",
    val parentId: String? = null,
    val startYear: Long = 0L,
    val endYear: Long = 0L,
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
    /** 所属分期的完整年份区间文本。 */
    val yearRangeText: String
        get() = when {
            startDateText.isNotEmpty() && endDateText.isNotEmpty() -> "$startDateText — $endDateText"
            startDateText.isNotEmpty() -> startDateText
            endDateText.isNotEmpty() -> endDateText
            else -> ""
        }
}

/**
 * 学科事件，契约 §3。
 *
 * 在自然科学语境下，`event` 表示一次**发现 / 理论提出 / 技术突破 / 重大观测**。
 *
 * [yearEnd] 为 `null` 表示时间点事件；[importance] 取值 1..5。
 *
 * 年份用 Long 而非 Int，理由同 [Period]：需要容纳地质深时的绝对年份。
 */
@Serializable
data class Event(
    val id: String = "",
    val name: String = "",
    val year: Long = 0L,
    val yearEnd: Long? = null,
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
    val span: Long
        get() = (yearEnd ?: year) - year

    /** 时间轴色条绘制所需的起点/终点。 */
    val spanStart: Long get() = year
    val spanEnd: Long get() = yearEnd ?: year
}

/**
 * 科学家 / 关键人物，契约 §4。
 *
 * [birthYear] / [deathYear] 为 `null` 表示不详。年份用 Long，理由同 [Period]。
 */
@Serializable
data class Figure(
    val id: String = "",
    val name: String = "",
    val alias: String = "",
    val birthYear: Long? = null,
    val deathYear: Long? = null,
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
 * 自然科学内容以 `scientific` / `technology` / `exploration` / `reform` 为主，
 * 其余分类用于人文学科交叉与事故、灾难类事件。
 */
enum class EventCategory(val value: String, val label: String) {
    POLITICAL("political", "政治"),
    MILITARY("military", "军事"),
    ECONOMIC("economic", "经济"),
    CULTURAL("cultural", "文化"),
    SCIENTIFIC("scientific", "科学发现"),
    SOCIAL("social", "社会"),
    RELIGIOUS("religious", "宗教"),
    ART("art", "艺术"),
    LITERATURE("literature", "文学"),
    EDUCATION("education", "教育"),
    TECHNOLOGY("technology", "技术"),
    EXPLORATION("exploration", "探索/观测"),
    CONFLICT("conflict", "冲突"),
    TREATY("treaty", "条约/协作"),
    REFORM("reform", "理论变革"),
    DYNASTY("dynasty", "奠基/更替"),
    CROSS_CIVILIZATION("cross-civilization", "跨学科交流"),
    DISASTER("disaster", "灾难/事故"),
    HEALTH("health", "医学/健康"),
    ECONOMY_CRISIS("economy-crisis", "危机"),
    LEGEND("legend", "传说/假说"),
    ARCHAEOLOGY("archaeology", "考古/遗址"),
    ;

    companion object {
        private val byValue = entries.associateBy { it.value }

        /** 未知分类回退到 [SCIENTIFIC]，不会抛异常。 */
        fun from(value: String): EventCategory = byValue[value] ?: SCIENTIFIC
    }
}

/**
 * 搜索结果聚合，跨分期 / 事件 / 人物三类实体匹配。
 */
data class SearchResult(
    val periods: List<Period> = emptyList(),
    val events: List<Event> = emptyList(),
    val figures: List<Figure> = emptyList(),
) {
    val isEmpty: Boolean get() = periods.isEmpty() && events.isEmpty() && figures.isEmpty()
    val total: Int get() = periods.size + events.size + figures.size
}
