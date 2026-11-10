package com.historyatlas.app.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * [splitByChronology] 的分组逻辑测试。
 *
 * 目标：把顶层时期分成「编年主干」与「专题补充」两组，
 * 使得跨朝代专题、区域专题不会被误当成编年主干。
 */
class SplitByChronologyTest {

    private fun p(id: String, start: Int, end: Int, vararg tags: String) = Period(
        id = id, name = id, startYear = start, endYear = end, tags = tags.toList(),
    )

    @Test
    fun `空列表返回两个空列表`() {
        val (main, extra) = splitByChronology(emptyList())
        assertTrue(main.isEmpty())
        assertTrue(extra.isEmpty())
    }

    @Test
    fun `时间不重叠的时期全部进入主干`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("a", -221, -207),
                p("b", -202, 220),
                p("c", 221, 589),
            ),
        )
        assertEquals(listOf("a", "b", "c"), main.map { it.id })
        assertTrue(extra.isEmpty(), "不重叠的时期不应进入补充组")
    }

    @Test
    fun `主干按起始年排序`() {
        val (main, _) = splitByChronology(
            listOf(
                p("late", 100, 200),
                p("early", -100, -50),
                p("mid", 0, 50),
            ),
        )
        assertEquals(listOf("early", "mid", "late"), main.map { it.id })
    }

    @Test
    fun `边界年份相接不算重叠`() {
        // 秦结束于 -207，汉开始于 -206 → 相接但不是重叠
        val (main, extra) = splitByChronology(
            listOf(p("qin", -221, -207), p("han", -206, 220)),
        )
        assertEquals(listOf("qin", "han"), main.map { it.id })
        assertTrue(extra.isEmpty())
    }

    @Test
    fun `边界重合不视为重叠`() {
        // 秦结束于 -207，汉开始于 -202，中间有空隙 → 属于主干
        val (main, extra) = splitByChronology(
            listOf(p("qin", -221, -207), p("han", -202, 220)),
        )
        assertEquals(2, main.size)
        assertTrue(extra.isEmpty())
    }

    // ------------------------------------------------------------------
    // 第 1 层：显式标注
    // ------------------------------------------------------------------

    @Test
    fun `显式标注区域专题的时期直接进入补充组`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("rome", -753, 476),
                p("europe", -500, 1500, "区域专题"),
            ),
        )
        assertEquals(listOf("rome"), main.map { it.id })
        assertEquals(listOf("europe"), extra.map { it.id })
    }

    @Test
    fun `显式标注跨朝代专题的时期进入补充组`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("han", -202, 220),
                p("topic", -206, 589, "跨朝代"),
            ),
        )
        assertEquals(listOf("han"), main.map { it.id })
        assertEquals(listOf("topic"), extra.map { it.id })
    }

    // ------------------------------------------------------------------
    // 第 2 层：包含关系
    // ------------------------------------------------------------------

    @Test
    fun `被完全包含的时期进入补充组`() {
        // long 覆盖 short → short 是被包裹项，进补充组
        val (main, extra) = splitByChronology(
            listOf(
                p("long", -221, 220),
                p("short", -100, -50),
            ),
        )
        assertEquals(listOf("long"), main.map { it.id })
        assertEquals(listOf("short"), extra.map { it.id })
    }

    @Test
    fun `跨度更长的跨朝代专题不会挤掉正统朝代`() {
        // 「三国两晋南北朝」跨度远大于「汉」，但它才是补充项
        val (main, extra) = splitByChronology(
            listOf(
                p("han", -202, 220),
                p("three-kingdoms", 220, 589),
                p("topic", -206, 589, "跨朝代专题"),
            ),
        )
        assertEquals(listOf("han", "three-kingdoms"), main.map { it.id })
        assertEquals(listOf("topic"), extra.map { it.id })
    }

    @Test
    fun `colorKey 为 purple 的时期视为跨朝代专题`() {
        val topic = Period(
            id = "topic", name = "专题", startYear = -206, endYear = 589,
            colorKey = "purple",
        )
        val (main, extra) = splitByChronology(
            listOf(
                p("han", -202, 220),
                p("three-kingdoms", 220, 589),
                topic,
            ),
        )
        assertEquals(listOf("han", "three-kingdoms"), main.map { it.id })
        assertEquals(listOf("topic"), extra.map { it.id })
    }

    @Test
    fun `包含关系判定要求跨度严格更大`() {
        // 同起同止的两个时期互不包含，按重叠处理
        val (main, extra) = splitByChronology(
            listOf(
                p("a", -100, 100),
                p("b", -100, 100),
            ),
        )
        assertEquals(1, main.size)
        assertEquals(1, extra.size)
    }

    // ------------------------------------------------------------------
    // 第 3 层：重叠兜底
    // ------------------------------------------------------------------

    @Test
    fun `部分重叠且互不包含的时期后者进入补充组`() {
        // x 与 y 区间部分交叠且互不包含 → 先进入的进主干，另一个进补充组
        val (main, extra) = splitByChronology(
            listOf(
                p("x", -50, 20),
                p("y", 0, 50),
            ),
        )
        assertEquals(1, main.size)
        assertEquals(1, extra.size)
        assertEquals(setOf("x", "y"), (main.map { it.id } + extra.map { it.id }).toSet())
    }

    @Test
    fun `多个时期与同一主干重叠时都进入补充组`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("main", -100, 100),
                p("x", -50, -10),
                p("y", 0, 50),
            ),
        )
        assertEquals(listOf("main"), main.map { it.id })
        assertEquals(setOf("x", "y"), extra.map { it.id }.toSet())
    }

    @Test
    fun `覆盖多个互不重叠下位朝代的上位时期仍进主干`() {
        // 纯几何无法区分「统辖两朝的上位政权」与「打包式专题」，
        // 因此这里以「上位时期进主干」为准；专题需由数据方显式标注。
        val (main, extra) = splitByChronology(
            listOf(
                p("main", -100, 100),
                p("x", -90, -10),
                p("y", 10, 90),
            ),
        )
        assertEquals(listOf("main"), main.map { it.id })
        assertEquals(setOf("x", "y"), extra.map { it.id }.toSet())
    }

    @Test
    fun `补充组不参与后续重叠判定`() {
        // x 与 y 彼此重叠，两者都与 main 重叠 → 两者都进补充组，
        // 且不应因为彼此重叠而被再次剔除
        val (main, extra) = splitByChronology(
            listOf(
                p("main", -100, 100),
                p("x", -50, 20),
                p("y", 0, 50),
            ),
        )
        assertEquals(1, main.size)
        assertEquals(2, extra.size)
        val all = (main.map { it.id } + extra.map { it.id }).toSet()
        assertEquals(setOf("main", "x", "y"), all)
    }

    @Test
    fun `所有时期都会被分配到两组之一`() {
        val input = listOf(
            p("a", -221, -207),
            p("b", -202, 220),
            p("c", 221, 589),
            p("d", -206, 589, "专题"),
            p("e", -100, 100),
            p("f", -50, 20),
        )
        val (main, extra) = splitByChronology(input)
        val all = (main.map { it.id } + extra.map { it.id }).toSet()
        assertEquals(input.map { it.id }.toSet(), all, "不应有时期被丢弃")
        assertEquals(input.size, main.size + extra.size, "不应有时期被重复分配")
    }
}
