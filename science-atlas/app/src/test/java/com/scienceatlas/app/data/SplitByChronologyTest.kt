package com.scienceatlas.app.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * [splitByChronology] 的分组逻辑测试。
 *
 * 目标：把顶层分期分成「编年主干」与「专题补充」两组，
 * 使得跨尺度专题、理论视角专题不会被误当成编年主干。
 */
class SplitByChronologyTest {

    private fun p(id: String, start: Long, end: Long, vararg tags: String) = Period(
        id = id, name = id, startYear = start, endYear = end, tags = tags.toList(),
    )

    @Test
    fun `空列表返回两个空列表`() {
        val (main, extra) = splitByChronology(emptyList())
        assertTrue(main.isEmpty())
        assertTrue(extra.isEmpty())
    }

    @Test
    fun `时间不重叠的分期全部进入主干`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("a", -3000, -500),
                p("b", -450, 1500),
                p("c", 1543, 1900),
            ),
        )
        assertEquals(listOf("a", "b", "c"), main.map { it.id })
        assertTrue(extra.isEmpty(), "不重叠的分期不应进入补充组")
    }

    @Test
    fun `主干按起始年排序`() {
        val (main, _) = splitByChronology(
            listOf(
                p("late", 1900, 2000),
                p("early", -2000, -1500),
                p("mid", 0, 500),
            ),
        )
        assertEquals(listOf("early", "mid", "late"), main.map { it.id })
    }

    @Test
    fun `边界年份相接不算重叠`() {
        // 古典物理结束于 1900，相对论开始于 1905 → 相接但不是重叠
        val (main, extra) = splitByChronology(
            listOf(p("classical", 1687, 1900), p("relativity", 1905, 1970)),
        )
        assertEquals(listOf("classical", "relativity"), main.map { it.id })
        assertTrue(extra.isEmpty())
    }

    @Test
    fun `边界重合不视为重叠`() {
        // 古典物理结束于 1900，相对论开始于 1900，中间有空隙 → 属于主干
        val (main, extra) = splitByChronology(
            listOf(p("classical", 1687, 1900), p("relativity", 1905, 1970)),
        )
        assertEquals(2, main.size)
        assertTrue(extra.isEmpty())
    }

    // ------------------------------------------------------------------
    // 第 1 层：显式标注
    // ------------------------------------------------------------------

    @Test
    fun `显式标注区域专题的分期直接进入补充组`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("geo-modern", 1900, 2000),
                p("topic-region", -500, 1500, "区域专题"),
            ),
        )
        assertEquals(listOf("geo-modern"), main.map { it.id })
        assertEquals(listOf("topic-region"), extra.map { it.id })
    }

    @Test
    fun `显式标注跨尺度专题的分期进入补充组`() {
        val (main, extra) = splitByChronology(
            listOf(
                p("phy-classical", 1687, 1900),
                p("topic-scale", -400, 2000, "跨尺度"),
            ),
        )
        assertEquals(listOf("phy-classical"), main.map { it.id })
        assertEquals(listOf("topic-scale"), extra.map { it.id })
    }

    @Test
    fun `显式标注编年主干的分期无条件进主干`() {
        // 史实本身就有合理重叠（古典力学与热学在 19 世纪交叠），
        // 早先用重叠判据会把主干分期误判为专题并藏起来。
        val (main, extra) = splitByChronology(
            listOf(
                p("a", 1687, 1900, "编年主干"),
                p("b", 1700, 1900),
            ),
        )
        assertTrue(main.any { it.id == "a" }, "显式标注编年主干的分期必须在主干里")
        assertEquals(2, (main + extra).size, "不应有分期被丢弃")
    }

    // ------------------------------------------------------------------
    // 第 2 层：包含关系
    // ------------------------------------------------------------------

    @Test
    fun `被完全包含的分期进入补充组`() {
        // long 覆盖 short → short 是被包裹项，进补充组
        val (main, extra) = splitByChronology(
            listOf(
                p("long", -3000, 2000),
                p("short", -100, -50),
            ),
        )
        assertEquals(listOf("long"), main.map { it.id })
        assertEquals(listOf("short"), extra.map { it.id })
    }

    @Test
    fun `跨度更长的专题不会挤掉正统分期`() {
        // 「地质年代」跨度远大于「古生代」，但它才是补充项
        val (main, extra) = splitByChronology(
            listOf(
                p("geo-paleozoic", -541, -252),
                p("geo-mesozoic", -252, -66),
                p("topic", -4600, 2000, "跨尺度专题"),
            ),
        )
        assertEquals(listOf("geo-paleozoic", "geo-mesozoic"), main.map { it.id })
        assertEquals(listOf("topic"), extra.map { it.id })
    }

    @Test
    fun `colorKey 为 purple 的分期视为跨尺度专题`() {
        val topic = Period(
            id = "topic", name = "专题", startYear = -4600, endYear = 2000,
            colorKey = "purple",
        )
        val (main, extra) = splitByChronology(
            listOf(
                p("geo-paleozoic", -541, -252),
                p("geo-mesozoic", -252, -66),
                topic,
            ),
        )
        assertEquals(listOf("geo-paleozoic", "geo-mesozoic"), main.map { it.id })
        assertEquals(listOf("topic"), extra.map { it.id })
    }

    @Test
    fun `包含关系判定要求跨度严格更大`() {
        // 同起同止的两个分期互不包含，按重叠处理
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
    fun `部分重叠且互不包含的分期后者进入补充组`() {
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
    fun `多个分期与同一主干重叠时都进入补充组`() {
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
    fun `覆盖多个互不重叠下位分期的上位分期仍进主干`() {
        // 纯几何无法区分「统辖两个阶段的上位分期」与「打包式专题」，
        // 因此这里以「上位分期进主干」为准；专题需由数据方显式标注。
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
    fun `同一分期不会同时出现在两组`() {
        // 回归测试：上位分期曾因被处理两次而同时进主干与补充组。
        val input = listOf(
            p("long", -3000, 2000),
            p("short", -100, -50),
            p("main", -100, 100),
            p("x", -50, 20),
            p("y", 0, 50),
        )
        val (main, extra) = splitByChronology(input)
        val mainIds = main.map { it.id }
        val extraIds = extra.map { it.id }
        assertTrue(
            mainIds.intersect(extraIds.toSet()).isEmpty(),
            "同一分期不得同时出现在两组：main=$mainIds extra=$extraIds",
        )
        assertEquals(
            input.map { it.id }.toSet(),
            (mainIds + extraIds).toSet(),
            "分组不得丢失或重复分配分期",
        )
    }

    @Test
    fun `分组不会丢失任何分期`() {
        val input = listOf(
            p("a", -3000, -500),
            p("b", -450, 1500),
            p("c", 1543, 1900),
            p("topic", -4600, 2000, "专题"),
            p("d", 1900, 2000),
        )
        val (main, extra) = splitByChronology(input)
        val outIds = (main.map { it.id } + extra.map { it.id }).toSet()
        assertEquals(input.map { it.id }.toSet(), outIds, "分组不得丢失分期")
    }
}
