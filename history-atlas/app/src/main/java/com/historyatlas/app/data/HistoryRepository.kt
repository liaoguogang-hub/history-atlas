package com.historyatlas.app.data

import android.content.Context
import com.historyatlas.app.ui.theme.ColorKeys
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json

/**
 * 把一批顶层时期按「编年主干 / 专题补充」分组。
 *
 * - **主干（main）**：构成连续编年主线的时期，按起始年排序。
 * - **补充（extra）**：跨朝代专题、区域专题、并行政权等无法排进主线的时期，
 *   单独成组展示。
 *
 * 判定分三层，从可靠到兜底：
 * 1. **显式标注**（最可靠）：数据契约 §6 规定 `colorKey = "purple"` 表示
 *    「跨朝代/专题」；`tags` 中的「区域专题」「跨朝代」「专题」同理。
 *    这类时期直接归入补充组。
 * 2. **包含关系**：若 A 的时间区间完全覆盖 B（跨度也更大），则 A 是上位时期、
 *    B 是被包裹项。A 先进主干占位，B 因与 A 区间重叠而归入补充组。
 * 3. **重叠兜底**：剩下的时期若与已接纳的主干在区间内部重叠（边界相接不算），
 *    归入补充组。
 *
 * 说明：纯几何无法区分「一个统辖两朝的上位政权」与「把两段历史打包的专题」，
 * 因此专题的判定以数据方的显式标注为准，几何规则只作兜底。
 *
 * @param periods 时期列表，通常是 [HistoryRepository.topLevelPeriods] 的结果。
 * @return `Pair(主干列表, 补充列表)`，可直接用解构语法取出。
 */
fun splitByChronology(periods: List<Period>): Pair<List<Period>, List<Period>> {
    if (periods.isEmpty()) return emptyList<Period>() to emptyList()

    // ---- 第 1 层：显式标注的专题直接进补充组 ----
    // 数据契约 §6 规定：colorKey = "purple" 表示「跨朝代/专题」，
    // 这是数据方给出的权威信号；tags 里的「区域专题」「跨朝代」「专题」同理。
    val explicitlyExtra = periods.filter { period ->
        period.colorKey.trim().lowercase() == ColorKeys.PURPLE ||
            period.tags.any { tag -> EXPLICIT_EXTRA_TAG_KEYS.any { tag.contains(it) } }
    }
    val candidates = periods.filter { it !in explicitlyExtra }

    // ---- 第 1.5 层：显式标注「编年主干」的时期无条件进主干 ----
    // 不能靠「区间是否重叠」来推断主干：史实本身就有合理重叠
    // （隋唐 581 起而三国两晋南北朝到 589 止；宋辽金 916 起而五代十国到 979 止），
    // 早先用重叠判据会把隋唐、宋辽金误判为专题并藏起来，
    // 表现为「查 1000 年时中国史是空的」。
    val explicitMain = candidates.filter { period ->
        period.tags.any { tag -> tag.contains(EXPLICIT_MAIN_TAG_KEY) }
    }
    val rest = candidates.filter { it !in explicitMain }

    // ---- 第 2 层：确定上位时期与被包裹项 ----
    // 包含关系：outer 完全覆盖 inner，且跨度严格更大
    fun covers(outer: Period, inner: Period): Boolean =
        outer !== inner &&
            outer.startYear <= inner.startYear && outer.endYear >= inner.endYear &&
            (outer.endYear - outer.startYear) > (inner.endYear - inner.startYear)

    // 覆盖了其它候选者的时期是上位时期（wrapper），需要先占位进入主干。
    val wrappers = rest.filter { outer -> rest.any { inner -> covers(outer, inner) } }

    // ---- 第 3 层：贪心选出互不重叠的主干 ----
    val main = mutableListOf<Period>().apply { addAll(explicitMain) }
    val extra = mutableListOf<Period>().apply { addAll(explicitlyExtra) }

    // 先放「包含者」（上位时期）：它们是上位单位，需要先占位，
    // 否则会被自己的下位朝代顶掉。后放普通时期。
    for (period in wrappers + rest) {
        // 仅在边界年份相接不算重叠（如秦 -221..-207 与汉 -202..220 之间有空隙）
        val conflict = main.any { existing -> overlaps(period, existing) }
        if (conflict) {
            extra += period
        } else {
            main += period
        }
    }

    val mainSorted = main.sortedWith(compareBy({ it.startYear }, { it.endYear }, { it.name }))
    val extraSorted = extra.sortedWith(compareBy({ it.startYear }, { it.endYear }, { it.name }))
    return mainSorted to extraSorted
}

/**
 * 数据方在 `period.tags` 中使用这些关键词时，该时期会被
 * [splitByChronology] 归入「专题补充」组。
 */
private val EXPLICIT_EXTRA_TAG_KEYS = listOf("区域专题", "跨朝代", "专题")

/**
 * 数据方在 `period.tags` 中使用这个关键词时，该时期**无条件**归入编年主干。
 * 它比「区间是否重叠」更权威：史实里的合理重叠不应导致朝代被藏起来。
 */
private val EXPLICIT_MAIN_TAG_KEY = "编年主干"

/**
 * 两个时期的时间区间是否在**内部**重叠。
 *
 * 仅在边界年份相接不算重叠（如秦 -221..-207 与汉 -206..220 在 -207/-206 相接）。
 */
private fun overlaps(a: Period, b: Period): Boolean =
    a.startYear < b.endYear && b.startYear < a.endYear

/**
 * 历史数据仓库：从 assets 读取 `data/china.json` 与 `data/world.json`，
 * 建立 id 索引，并对悬空引用做容错剔除。
 *
 * 设计要点：
 * 1. **懒加载 + 单次解析**：每个 scope 的数据只在首次访问时解析并缓存。
 * 2. **引用容错**：解析后建立 id → 实体 的 Map；指向不存在 id 的引用
 *    在清洗阶段被剔除（而不是在 UI 层崩溃）。
 * 3. **无网络**：全部数据来自打包进 APK 的 assets，纯离线可用。
 */
class HistoryRepository private constructor(
    private val appContext: Context?,
    /** 直接注入数据集（供测试与预览使用）；为空时从 assets 懒加载。 */
    private val injectedDatasets: Map<String, HistoryDataset> = emptyMap(),
) {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        explicitNulls = false
    }

    /** scope → 数据集，懒加载。 */
    private val datasets = java.util.concurrent.ConcurrentHashMap<String, HistoryDataset>()

    /** scope → 清洗后的索引缓存。 */
    private val indexes = java.util.concurrent.ConcurrentHashMap<String, ScopeIndex>()

    /** 数据加载状态，供 UI 观察。 */
    private val _loadState = MutableStateFlow<LoadState>(LoadState.Idle)
    val loadState: StateFlow<LoadState> = _loadState.asStateFlow()

    /** 全部可用的 scope。 */
    val availableScopes: List<String> get() = listOf(SCOPE_CHINA, SCOPE_WORLD)

    // ---------------------------------------------------------------------
    // 数据加载
    // ---------------------------------------------------------------------

    private fun dataset(scope: String): HistoryDataset = datasets.getOrPut(scope) {
        _loadState.value = LoadState.Loading(scope)
        // 注入的数据集优先（测试 / 预览）
        injectedDatasets[scope]?.let { injected ->
            return injected.copy(scope = injected.scope.ifEmpty { scope })
        }
        val context = appContext
        val loaded = if (context == null) {
            _loadState.value = LoadState.Failed(scope, "无可用的 Context")
            return HistoryDataset(version = 1, scope = scope)
        } else {
            runCatching {
                val path = assetPath(scope)
                val text = context.assets.open(path).bufferedReader().use { it.readText() }
                json.decodeFromString(HistoryDataset.serializer(), text)
            }.getOrElse { error ->
                _loadState.value = LoadState.Failed(scope, error.message ?: error::class.java.simpleName)
                // 缺文件 / 解析失败时返回空数据集，不让 App 崩溃
                return HistoryDataset(version = 1, scope = scope)
            }
        }
        loaded.copy(scope = loaded.scope.ifEmpty { scope })
    }

    private fun assetPath(scope: String): String = when (scope) {
        SCOPE_CHINA -> "data/china.json"
        SCOPE_WORLD -> "data/world.json"
        else -> "data/$scope.json"
    }

    private fun index(scope: String): ScopeIndex = indexes.getOrPut(scope) {
        ScopeIndex.build(dataset(scope))
    }

    /** 主动预加载某个 scope（可选，用于首屏提前解析）。 */
    fun preload(scope: String) {
        index(scope)
        _loadState.value = LoadState.Ready(scope)
    }

    /**
     * 在 IO 线程预加载某个 scope。
     *
     * 数据文件可达数 MB，同步解析会阻塞首帧，因此首屏预热必须放到后台线程。
     *
     * @param scope 目标 scope。
     */
    suspend fun preloadAsync(scope: String) {
        withContext(Dispatchers.IO) {
            index(scope)
        }
        _loadState.value = LoadState.Ready(scope)
    }

    /** 主动预加载全部 scope（在后台线程）。 */
    suspend fun preloadAllAsync() {
        availableScopes.forEach { preloadAsync(it) }
    }

    /**
     * 取统计信息，但不触发同步解析。
     *
     * 若该 scope 尚未加载，返回空统计（而非在调用线程解析整个数据集）。
     * 供首屏使用，避免主线程卡顿。
     */
    fun statisticsPeek(scope: String): Statistics {
        val idx = indexes[scope] ?: return Statistics(scope = scope)
        return Statistics(
            scope = scope,
            periodCount = idx.periods.size,
            eventCount = idx.events.size,
            figureCount = idx.figures.size,
        )
    }

    // ---------------------------------------------------------------------
    // 时期查询
    // ---------------------------------------------------------------------

    /** 某 scope 下的全部时期，按起始年排序。 */
    fun periods(scope: String): List<Period> = index(scope).periods

    /** 某 scope 下的顶层时期（`parentId` 为 null 或指向不存在节点）。 */
    fun topLevelPeriods(scope: String): List<Period> = index(scope).topLevelPeriods

    /** 直接子时期。 */
    fun childrenOf(periodId: String, scope: String): List<Period> =
        index(scope).childrenByParent[periodId].orEmpty()

    /** 按 id 取时期。 */
    fun period(id: String, scope: String): Period? = index(scope).periodById[id]

    /** 时期的全部后代（不含自身），广度优先。 */
    fun descendantsOf(periodId: String, scope: String): List<Period> {
        val idx = index(scope)
        val out = mutableListOf<Period>()
        val queue = ArrayDeque<String>()
        queue.add(periodId)
        val seen = mutableSetOf(periodId)
        while (queue.isNotEmpty()) {
            val current = queue.removeFirst()
            for (child in idx.childrenByParent[current].orEmpty()) {
                if (seen.add(child.id)) {
                    out += child
                    queue.add(child.id)
                }
            }
        }
        return out
    }

    /** 时期及其全部后代的 id 集合。 */
    fun periodSubtreeIds(periodId: String, scope: String): Set<String> =
        (setOf(periodId) + descendantsOf(periodId, scope).map { it.id })

    // ---------------------------------------------------------------------
    // 事件查询
    // ---------------------------------------------------------------------

    /** 某 scope 下的全部事件，按年份排序。 */
    fun eventsOfScope(scope: String): List<Event> = index(scope).events

    /** 直接挂在该时期下的事件。 */
    fun eventsOf(periodId: String, scope: String): List<Event> =
        index(scope).eventsByPeriod[periodId].orEmpty()

    /** 该时期及其所有后代时期下的事件（时间轴用）。 */
    fun eventsOfSubtree(periodId: String, scope: String): List<Event> {
        val idx = index(scope)
        val ids = periodSubtreeIds(periodId, scope)
        return idx.events.filter { it.periodId in ids }.sortedBy { it.year }
    }

    /** 按 id 取事件。 */
    fun event(id: String, scope: String): Event? = index(scope).eventById[id]

    /** 按分类筛选事件。 */
    fun eventsByCategory(category: EventCategory, scope: String): List<Event> =
        eventsOfScope(scope).filter { it.category == category.value }

    // ---------------------------------------------------------------------
    // 人物查询
    // ---------------------------------------------------------------------

    /** 某 scope 下的全部人物。 */
    fun figuresOfScope(scope: String): List<Figure> = index(scope).figures

    /** 直接挂在该时期下的人物。 */
    fun figuresOf(periodId: String, scope: String): List<Figure> =
        index(scope).figuresByPeriod[periodId].orEmpty()

    /** 按 id 取人物。 */
    fun figure(id: String, scope: String): Figure? = index(scope).figureById[id]

    /** 批量解析人物 id，忽略解析不到的（悬空引用已在清洗阶段剔除）。 */
    fun resolveFigureIds(ids: List<String>, scope: String): List<Figure> {
        val idx = index(scope)
        return ids.mapNotNull { idx.figureById[it] }
    }

    /** 批量解析事件 id，忽略解析不到的。 */
    fun resolveEventIds(ids: List<String>, scope: String): List<Event> {
        val idx = index(scope)
        return ids.mapNotNull { idx.eventById[it] }
    }

    // ---------------------------------------------------------------------
    // 搜索
    // ---------------------------------------------------------------------

    /**
     * 跨时期 / 事件 / 人物匹配 name / summary / tags（也匹配 alias、detail、biography）。
     * 查询词为空时返回空结果。
     */
    fun search(query: String, scope: String): SearchResult {
        val q = query.trim()
        if (q.isEmpty()) return SearchResult()
        val needle = q.lowercase()

        val idx = index(scope)
        val matchedPeriods = idx.periods.filter { p ->
            p.name.lowercase().contains(needle) ||
                p.alias.lowercase().contains(needle) ||
                p.summary.lowercase().contains(needle) ||
                p.tags.any { it.lowercase().contains(needle) } ||
                p.startDateText.contains(q) ||
                p.endDateText.contains(q)
        }
        val matchedEvents = idx.events.filter { e ->
            e.name.lowercase().contains(needle) ||
                e.summary.lowercase().contains(needle) ||
                e.detail.lowercase().contains(needle) ||
                e.location.lowercase().contains(needle) ||
                e.tags.any { it.lowercase().contains(needle) } ||
                e.dateText.contains(q)
        }
        val matchedFigures = idx.figures.filter { f ->
            f.name.lowercase().contains(needle) ||
                f.alias.lowercase().contains(needle) ||
                f.summary.lowercase().contains(needle) ||
                f.biography.lowercase().contains(needle) ||
                f.role.lowercase().contains(needle) ||
                f.tags.any { it.lowercase().contains(needle) } ||
                f.lifeText.contains(q)
        }
        return SearchResult(
            periods = matchedPeriods,
            events = matchedEvents,
            figures = matchedFigures,
        )
    }

    // ---------------------------------------------------------------------
    // 统计
    // ---------------------------------------------------------------------

    fun statistics(scope: String): Statistics {
        val idx = index(scope)
        return Statistics(
            scope = scope,
            periodCount = idx.periods.size,
            eventCount = idx.events.size,
            figureCount = idx.figures.size,
        )
    }

    /** 载入状态。 */
    sealed interface LoadState {
        data object Idle : LoadState
        data class Loading(val scope: String) : LoadState
        data class Ready(val scope: String) : LoadState
        data class Failed(val scope: String, val message: String) : LoadState
    }

    /** 单个 scope 的统计数据。 */
    data class Statistics(
        val scope: String = "",
        val periodCount: Int = 0,
        val eventCount: Int = 0,
        val figureCount: Int = 0,
    )

    /**
     * 清洗并索引后的数据集。
     *
     * 所有引用（parentId / periodId / keyFigures / relatedEvents / relatedFigures /
     * event.figures）在清洗阶段被校验，指向不存在 id 的条目被剔除。
     */
    private class ScopeIndex(
        val periods: List<Period>,
        val events: List<Event>,
        val figures: List<Figure>,
        val periodById: Map<String, Period>,
        val eventById: Map<String, Event>,
        val figureById: Map<String, Figure>,
        val childrenByParent: Map<String, List<Period>>,
        val topLevelPeriods: List<Period>,
        val eventsByPeriod: Map<String, List<Event>>,
        val figuresByPeriod: Map<String, List<Figure>>,
    ) {
        companion object {
            fun build(raw: HistoryDataset): ScopeIndex {
                // 1. 去重（保留首次出现）
                val periodById = LinkedHashMap<String, Period>()
                raw.periods.forEach { p -> if (p.id.isNotEmpty()) periodById.putIfAbsent(p.id, p) }
                val eventById = LinkedHashMap<String, Event>()
                raw.events.forEach { e -> if (e.id.isNotEmpty()) eventById.putIfAbsent(e.id, e) }
                val figureById = LinkedHashMap<String, Figure>()
                raw.figures.forEach { f -> if (f.id.isNotEmpty()) figureById.putIfAbsent(f.id, f) }

                // 2. 清洗时期：parentId 悬空 → 视为顶层；并剔除自引用
                val cleanedPeriods = periodById.values.map { p ->
                    val parent = p.parentId
                    val validParent = when {
                        parent.isNullOrEmpty() -> null
                        parent == p.id -> null
                        !periodById.containsKey(parent) -> null
                        else -> parent
                    }
                    p.copy(
                        parentId = validParent,
                        keyFigures = p.keyFigures.filter { figureById.containsKey(it) },
                        relatedEvents = p.relatedEvents.filter { eventById.containsKey(it) },
                    )
                }
                val cleanedPeriodIds = cleanedPeriods.mapTo(HashSet()) { it.id }

                // 3. 清洗事件：periodId 悬空的事件整体丢弃（契约要求 periodId 必须存在）
                val cleanedEvents = eventById.values
                    .filter { it.periodId.isNotEmpty() && cleanedPeriodIds.contains(it.periodId) }
                    .map { e ->
                        e.copy(figures = e.figures.filter { figureById.containsKey(it) })
                    }

                // 4. 清洗人物：periodId 悬空的人物整体丢弃
                val cleanedFigures = figureById.values
                    .filter { it.periodId.isNotEmpty() && cleanedPeriodIds.contains(it.periodId) }
                    .map { f ->
                        f.copy(
                            relatedEvents = f.relatedEvents.filter { eventById.containsKey(it) },
                            relatedFigures = f.relatedFigures.filter { figureById.containsKey(it) },
                        )
                    }

                // 5. 建立索引
                val finalPeriodById = cleanedPeriods.associateBy { it.id }
                val finalEventById = cleanedEvents.associateBy { it.id }
                val finalFigureById = cleanedFigures.associateBy { it.id }

                val childrenByParent = cleanedPeriods
                    .filter { it.parentId != null }
                    .groupBy { it.parentId!! }
                    .mapValues { (_, list) -> list.sortedWith(periodComparator) }

                val topLevelPeriods = cleanedPeriods
                    .filter { it.parentId == null }
                    .sortedWith(periodComparator)

                val eventsByPeriod = cleanedEvents
                    .groupBy { it.periodId }
                    .mapValues { (_, list) -> list.sortedBy { it.year } }

                val figuresByPeriod = cleanedFigures
                    .groupBy { it.periodId }

                return ScopeIndex(
                    periods = cleanedPeriods.sortedWith(periodComparator),
                    events = cleanedEvents.sortedWith(compareBy({ it.year }, { it.name })),
                    figures = cleanedFigures.sortedWith(compareBy({ it.birthYear ?: Int.MAX_VALUE }, { it.name })),
                    periodById = finalPeriodById,
                    eventById = finalEventById,
                    figureById = finalFigureById,
                    childrenByParent = childrenByParent,
                    topLevelPeriods = topLevelPeriods,
                    eventsByPeriod = eventsByPeriod,
                    figuresByPeriod = figuresByPeriod,
                )
            }

            private val periodComparator = compareBy<Period>({ it.startYear }, { it.endYear }, { it.name })
        }
    }

    companion object {
        const val SCOPE_CHINA = "china"
        const val SCOPE_WORLD = "world"

        @Volatile
        private var instance: HistoryRepository? = null

        /** 获取单例；首次调用需传入 applicationContext。 */
        fun getInstance(context: Context): HistoryRepository =
            instance ?: synchronized(this) {
                instance ?: HistoryRepository(context.applicationContext).also { instance = it }
            }

        /**
         * 用已有数据集构造一个仓库实例（不读 assets）。
         *
         * 仅供单元测试与 Compose 预览使用，不参与线上流程。
         */
        internal fun forTesting(datasets: Map<String, HistoryDataset>): HistoryRepository =
            HistoryRepository(appContext = null, injectedDatasets = datasets)
    }
}
