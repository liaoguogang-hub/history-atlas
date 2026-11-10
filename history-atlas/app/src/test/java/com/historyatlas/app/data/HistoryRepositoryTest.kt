package com.historyatlas.app.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

/**
 * 仓库层测试：验证**引用容错**与查询 API。
 *
 * 通过 `forTesting` 注入数据集，不依赖 Android Context 与 assets。
 */
class HistoryRepositoryTest {

    private val scope = HistoryRepository.SCOPE_CHINA

    /**
     * 构造一个包含各类「问题数据」的数据集：
     * - `p-root` 顶层时期
     * - `p-child` 正常子时期
     * - `p-orphan` parentId 悬空的时期（应被提升为顶层）
     * - `p-self` parentId 指向自身（应被置为 null）
     * - `p-dup` 与 `p-dup` 重复 id（应去重，保留首次）
     * - `e-good` periodId 有效
     * - `e-orphan` periodId 悬空（应被丢弃）
     * - `f-good` periodId 有效
     * - `f-orphan` periodId 悬空（应被丢弃）
     * - 各类悬空 id 引用
     */
    private fun dirtyDataset() = HistoryDataset(
        version = 1,
        scope = HistoryRepository.SCOPE_CHINA,
        periods = listOf(
            Period(id = "p-root", name = "根时期", startYear = -1000, endYear = 1000),
            Period(id = "p-child", name = "子时期", parentId = "p-root", startYear = -500, endYear = 0),
            Period(id = "p-orphan", name = "孤儿时期", parentId = "does-not-exist", startYear = 1, endYear = 2),
            Period(id = "p-self", name = "自引用时期", parentId = "p-self", startYear = 3, endYear = 4),
            Period(
                id = "p-dup", name = "重复时期", startYear = 5, endYear = 6,
                keyFigures = listOf("f-good", "f-missing"),
                relatedEvents = listOf("e-good", "e-missing"),
            ),
            Period(id = "p-dup", name = "重复时期-第二次", startYear = 5, endYear = 6),
        ),
        events = listOf(
            Event(
                id = "e-good", name = "有效事件", year = -100, periodId = "p-child",
                figures = listOf("f-good", "f-missing"),
            ),
            Event(id = "e-orphan", name = "孤儿事件", year = -50, periodId = "no-such-period"),
            Event(id = "e-nop", name = "无时期事件", year = -50, periodId = ""),
        ),
        figures = listOf(
            Figure(
                id = "f-good", name = "有效人物", periodId = "p-child",
                relatedEvents = listOf("e-good", "e-missing"),
                relatedFigures = listOf("f-other", "f-missing"),
            ),
            Figure(id = "f-other", name = "另一人物", periodId = "p-child"),
            Figure(id = "f-orphan", name = "孤儿人物", periodId = "no-such-period"),
        ),
    )

    private fun repo() = HistoryRepository.forTesting(mapOf(scope to dirtyDataset()))

    // ------------------------------------------------------------------
    // 引用容错
    // ------------------------------------------------------------------

    @Test
    fun `periodId 悬空的事件被丢弃而不是崩溃`() {
        val r = repo()
        assertNull(r.event("e-orphan", scope), "periodId 悬空的事件应被剔除")
        assertNull(r.event("e-nop", scope), "缺少 periodId 的事件应被剔除")
        assertNotNull(r.event("e-good", scope), "有效事件应保留")
        assertEquals(1, r.eventsOfScope(scope).size)
    }

    @Test
    fun `periodId 悬空的人物被丢弃`() {
        val r = repo()
        assertNull(r.figure("f-orphan", scope))
        assertNotNull(r.figure("f-good", scope))
        assertEquals(2, r.figuresOfScope(scope).size)
    }

    @Test
    fun `parentId 悬空的时期被提升为顶层`() {
        val r = repo()
        val orphan = r.period("p-orphan", scope)
        assertNotNull(orphan)
        assertNull(orphan.parentId, "parentId 悬空应置为 null")
        assertTrue(
            r.topLevelPeriods(scope).any { it.id == "p-orphan" },
            "被提升的时期应出现在顶层列表中",
        )
    }

    @Test
    fun `指向自身的 parentId 被清除以避免环`() {
        val r = repo()
        val self = r.period("p-self", scope)
        assertNotNull(self)
        assertNull(self.parentId, "自引用必须被清除")
    }

    @Test
    fun `重复 id 保留首次出现`() {
        val r = repo()
        val dup = r.period("p-dup", scope)
        assertNotNull(dup)
        assertEquals("重复时期", dup.name, "重复 id 应保留首次出现的条目")
    }

    @Test
    fun `时期中的悬空人物与事件引用被剔除`() {
        val r = repo()
        val dup = r.period("p-dup", scope)!!
        assertEquals(listOf("f-good"), dup.keyFigures, "悬空人物 id 应被剔除")
        assertEquals(listOf("e-good"), dup.relatedEvents, "悬空事件 id 应被剔除")
    }

    @Test
    fun `事件中的人物引用剔除悬空项`() {
        val r = repo()
        val good = r.event("e-good", scope)!!
        assertEquals(listOf("f-good"), good.figures)
    }

    @Test
    fun `人物的事件与人物引用剔除悬空项`() {
        val r = repo()
        val f = r.figure("f-good", scope)!!
        assertEquals(listOf("e-good"), f.relatedEvents)
        assertEquals(listOf("f-other"), f.relatedFigures)
    }

    // ------------------------------------------------------------------
    // 查询 API
    // ------------------------------------------------------------------

    @Test
    fun `时期树查询正确`() {
        val r = repo()
        assertEquals(1, r.childrenOf("p-root", scope).size)
        assertEquals("p-child", r.childrenOf("p-root", scope).first().id)
        assertTrue(r.topLevelPeriods(scope).any { it.id == "p-root" })

        val descendants = r.descendantsOf("p-root", scope)
        assertEquals(listOf("p-child"), descendants.map { it.id })
        assertEquals(setOf("p-root", "p-child"), r.periodSubtreeIds("p-root", scope))
    }

    @Test
    fun `事件按时期查询`() {
        val r = repo()
        assertEquals(1, r.eventsOf("p-child", scope).size)
        assertEquals("e-good", r.eventsOf("p-child", scope).first().id)
        assertEquals(0, r.eventsOf("p-root", scope).size)
    }

    @Test
    fun `子树事件查询包含后代时期的事件`() {
        val r = repo()
        assertEquals(1, r.eventsOfSubtree("p-root", scope).size)
        assertEquals(0, r.eventsOfSubtree("p-dup", scope).size)
    }

    @Test
    fun `人物按时期查询`() {
        val r = repo()
        assertEquals(2, r.figuresOf("p-child", scope).size)
        assertEquals(0, r.figuresOf("p-root", scope).size)
    }

    @Test
    fun `批量解析人物 id 忽略解析不到的`() {
        val r = repo()
        val resolved = r.resolveFigureIds(listOf("f-good", "f-missing", "f-other"), scope)
        assertEquals(listOf("f-good", "f-other"), resolved.map { it.id })
    }

    @Test
    fun `批量解析事件 id 忽略解析不到的`() {
        val r = repo()
        val resolved = r.resolveEventIds(listOf("e-good", "e-missing"), scope)
        assertEquals(listOf("e-good"), resolved.map { it.id })
    }

    @Test
    fun `搜索匹配时期事件人物的名称与标签`() {
        val r = repo()
        val byPeriod = r.search("根时期", scope)
        assertEquals(1, byPeriod.periods.size)
        assertEquals("p-root", byPeriod.periods.first().id)

        val byEvent = r.search("有效事件", scope)
        assertEquals(1, byEvent.events.size)

        val byFigure = r.search("有效人物", scope)
        assertEquals(1, byFigure.figures.size)

        val empty = r.search("   ", scope)
        assertTrue(empty.isEmpty, "空查询应返回空结果")
        assertEquals(0, empty.total)
    }

    @Test
    fun `搜索可以跨类型同时命中`() {
        val r = repo()
        val result = r.search("有效", scope)
        assertEquals(1, result.events.size)
        assertEquals(1, result.figures.size)
        assertEquals(2, result.total)
        assertTrue(!result.isEmpty)
    }

    @Test
    fun `统计信息反映清洗后的数量`() {
        val r = repo()
        val stats = r.statistics(scope)
        assertEquals(5, stats.periodCount, "去重后应剩 5 个时期")
        assertEquals(1, stats.eventCount, "清洗后应剩 1 个事件")
        assertEquals(2, stats.figureCount, "清洗后应剩 2 个人物")
    }

    @Test
    fun `重复访问不会重复解析`() {
        val r = repo()
        val first = r.eventsOfScope(scope)
        val second = r.eventsOfScope(scope)
        assertEquals(first.size, second.size)
        assertTrue(first === second, "缓存命中时应返回同一份列表实例")
    }

    @Test
    fun `空数据集不崩溃`() {
        val r = HistoryRepository.forTesting(mapOf(scope to HistoryDataset(scope = scope)))
        assertEquals(0, r.periods(scope).size)
        assertEquals(0, r.eventsOfScope(scope).size)
        assertEquals(0, r.figuresOfScope(scope).size)
        assertTrue(r.search("任意", scope).isEmpty)
    }
}
