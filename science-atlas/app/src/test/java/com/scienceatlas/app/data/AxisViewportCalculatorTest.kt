package com.scienceatlas.app.data

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * 时间轴默认视窗的回归测试。
 *
 * 这段测试的存在理由：地理学科的时间轴曾**整条刻度显示为「前 19 亿年」**，
 * 近现代事件全部挤成最右侧一个像素点。根因有两个：
 *
 *   1. 缩放下限 `MIN_PPY = 0.0008` 把跨度几十亿年的视窗强行收窄
 *   2. 默认视窗用「年份 2%~92% 分位」定位，对地质深时离群点没有抵抗力
 *
 * 修复后必须保证：视窗落在事件密集的年代区间，
 * 且多数事件可见。下面的测试用**仓库里的真实数据**做断言，
 * 避免用构造样本时把真实分布特征丢掉。
 */
class AxisViewportCalculatorTest {

    /** 画布宽度，取常见手机逻辑宽度（约 1080px 物理像素下的 CSS 宽度）。 */
    private val canvasWidth = 1080f

    private fun loadYears(file: String): List<Long> {
        val f = File("../../data-science/$file")
        assertTrue(f.isFile, "找不到数据文件：${f.absolutePath}")
        val json = kotlinx.serialization.json.Json {
            ignoreUnknownKeys = true
            isLenient = true
            coerceInputValues = true
            explicitNulls = false
        }
        val ds = json.decodeFromString(ScienceDataset.serializer(), f.readText())
        return ds.events.map { it.year }
    }

    // ------------------------------------------------------------------
    // 核心回归：地理
    // ------------------------------------------------------------------

    @Test
    fun `地理的默认视窗不落在地质深时`() {
        val years = loadYears("geo.json")
        val vp = AxisViewportCalculator.compute(years)

        // 视窗中心必须落在「前 10 亿年」之后——
        // 修复前落在前 19 亿年（-1949999005）。
        assertTrue(
            vp.centerYear > -1_000_000_000.0,
            "地理视窗中心仍在地质深时：${vp.centerYear}",
        )
    }

    @Test
    fun `地理的多数事件落在默认视窗内`() {
        val years = loadYears("geo.json")
        val vp = AxisViewportCalculator.compute(years)
        val visible = years.count {
            AxisViewportCalculator.isVisible(it, vp, canvasWidth)
        }
        // 修复前可见事件只有个位数（近现代全挤在右边缘一个像素）
        assertTrue(
            visible >= years.size / 2,
            "地理可见事件太少：$visible / ${years.size}（视窗中心 ${vp.centerYear}）",
        )
    }

    @Test
    fun `地理视窗跨度足以分辨近现代事件`() {
        val years = loadYears("geo.json")
        val vp = AxisViewportCalculator.compute(years)
        val half = AxisViewportCalculator.halfSpanYears(vp.pixelsPerYear, canvasWidth)
        // 视窗至少要能看到千年尺度，否则公元后的所有事件仍然重叠
        assertTrue(
            half >= 1000.0,
            "地理视窗半跨度只有 $half 年，近现代事件仍会重叠",
        )
    }

    // ------------------------------------------------------------------
    // 其余三学科不应受影响
    // ------------------------------------------------------------------

    @Test
    fun `天文物理化学的视窗落在近现代`() {
        listOf("astro.json", "physics.json", "chem.json").forEach { file ->
            val years = loadYears(file)
            val vp = AxisViewportCalculator.compute(years)
            assertTrue(
                vp.centerYear > 1000.0,
                "$file 的视窗中心不在近现代：${vp.centerYear}",
            )
            assertTrue(
                vp.centerYear < 2100.0,
                "$file 的视窗中心越过了现代：${vp.centerYear}",
            )
        }
    }

    @Test
    fun `天文物理化学的多数事件可见`() {
        listOf("astro.json", "physics.json", "chem.json").forEach { file ->
            val years = loadYears(file)
            val vp = AxisViewportCalculator.compute(years)
            val visible = years.count {
                AxisViewportCalculator.isVisible(it, vp, canvasWidth)
            }
            assertTrue(
                visible >= years.size * 3 / 4,
                "$file 可见事件太少：$visible / ${years.size}",
            )
        }
    }

    // ------------------------------------------------------------------
    // 边界与通用性质
    // ------------------------------------------------------------------

    @Test
    fun `空年份返回中性视窗`() {
        val vp = AxisViewportCalculator.compute(emptyList())
        assertEquals(0.0, vp.centerYear)
        assertTrue(vp.pixelsPerYear > 0f)
    }

    @Test
    fun `单一事件不崩溃且有最小跨度`() {
        val vp = AxisViewportCalculator.compute(listOf(1900L))
        assertEquals(1900.0, vp.centerYear)
        // 单点时跨度被兜底为 40 年（留白后 46.4 年），像素率不会趋于无穷
        assertTrue(vp.pixelsPerYear in 0f..3f, "像素率越界：${vp.pixelsPerYear}")
    }

    @Test
    fun `同一年份的多个事件不会让缩放失控`() {
        val vp = AxisViewportCalculator.compute(List(50) { 1900L })
        assertTrue(vp.pixelsPerYear in 0f..3f, "像素率越界：${vp.pixelsPerYear}")
    }

    @Test
    fun `像素率被限制在合法区间`() {
        // 超大跨度（万亿年）不应产生小于下限的像素率
        val vp = AxisViewportCalculator.compute(listOf(-1_000_000_000_000L, 0L, 1_000_000_000_000L))
        assertTrue(
            vp.pixelsPerYear >= AxisViewportCalculator.MIN_PPY,
            "像素率低于下限：${vp.pixelsPerYear}",
        )
        assertTrue(
            vp.pixelsPerYear <= 3f,
            "像素率高于上限：${vp.pixelsPerYear}",
        )
    }

    @Test
    fun `缩放下限足够小以容纳地质深时`() {
        // 回归：下限曾是 0.0008，导致地理视窗被收窄到 ±67 万年。
        // 现在下限必须小到能显示 46 亿年跨度。
        val half = AxisViewportCalculator.halfSpanYears(
            AxisViewportCalculator.MIN_PPY, canvasWidth,
        )
        assertTrue(
            half > 1_000_000_000.0,
            "缩放下限收得太紧，下限只能显示 ${half / 1e8} 亿年",
        )
    }

    @Test
    fun `计算结果与输入顺序无关`() {
        val years = loadYears("geo.json")
        val a = AxisViewportCalculator.compute(years)
        val b = AxisViewportCalculator.compute(years.reversed())
        assertEquals(a.centerYear, b.centerYear)
        assertEquals(a.pixelsPerYear, b.pixelsPerYear)
    }
}
