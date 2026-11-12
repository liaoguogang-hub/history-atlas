package com.scienceatlas.app.data

import com.scienceatlas.app.ui.AxisViewport

/**
 * 时间轴默认视窗的计算。
 *
 * 抽成独立纯函数是为了能脱离 Compose 做单元测试——
 * 这段逻辑出过一次严重 bug（地理学科的时间轴刻度全是「前 19 亿年」），
 * 必须有测试锁住。
 *
 * 背景：四个学科的年代尺度差异极大。
 *
 * | 学科 | 事件年代范围 | 跨度 |
 * |---|---|---|
 * | 地理 | -46 亿年 ~ 2004 年 | 约 46 亿年 |
 * | 天文 | 公元前 130 年 ~ 2000 年代 | 约 2000 年 |
 * | 物理 | 公元前 350 年 ~ 2000 年代 | 约 2000 年 |
 * | 化学 | 公元前 750 年 ~ 2000 年代 | 约 2000 年 |
 *
 * 地理的「地球形成」「大氧化事件」这类地质深时事件是**天然离群点**：
 * 55 条事件里有 11 条落在前 5 亿年之前，其余绝大多数集中在公元 1400 年之后。
 *
 * 早期实现取「年份 2%~92% 分位」定视窗，问题在于：
 * 分位数对离群点没有抵抗力——视窗中心落在前 19 亿年、跨度几十亿年，
 * 于是①刻度全部显示为「前 X 亿年」，②所有近现代事件挤成最右侧一个像素点，
 * 等于什么都看不见。
 */
object AxisViewportCalculator {

    /**
     * 缩放下限：每年最少占多少像素。
     *
     * **必须足够小**，否则地质深时这类跨度以「亿年」计的时间轴会被下限强行收窄：
     * 地理数据跨度约 39 亿年，1080px 下自然像素率约 2.77e-7。
     * 若下限设成 0.0008，视窗会被抬到 8e-4，可见区间只剩 ±67 万年，
     * 整条轴的刻度全部挤在「前 19 亿年」附近。
     *
     * 1e-9 对应 1080px 里显示约 1.08 万亿年，对任何真实数据都远够用。
     */
    const val MIN_PPY = 1e-9f

    /** 缩放上限：每年最多占多少像素。 */
    const val MAX_PPY = 400f

    /** 视窗最窄跨度（年）。避免所有事件挤在同一年时缩放失控。 */
    private const val MIN_SPAN_YEARS = 40.0

    /** 视窗两侧留白比例（每侧 8%，合计 16%）。 */
    private const val PADDING_RATIO = 1.16

    /** 参与离群点判定的最少样本数，低于此值直接用全量年份。 */
    private const val MIN_INLIER_SAMPLES = 4

    /**
     * 计算一组事件年份的默认视窗。
     *
     * @param years 事件年份，可乱序，可含重复。
     * @return 默认视窗；years 为空时返回以公元元年为中心的中性视窗。
     */
    fun compute(years: List<Long>): AxisViewport {
        if (years.isEmpty()) return AxisViewport(0.0, 0.5f)

        val sorted = years.sorted()
        fun quantile(p: Double): Double {
            val i = ((sorted.size - 1) * p).toInt().coerceIn(0, sorted.size - 1)
            return sorted[i].toDouble()
        }

        // IQR 离群点过滤：只保留 [Q1 - 1.5*IQR, Q3 + 1.5*IQR] 内的年份。
        // 地质深时事件会落在下界之外，从而不参与视窗定位。
        val q1 = quantile(0.25)
        val q3 = quantile(0.75)
        val iqr = q3 - q1
        val lowFence = q1 - 1.5 * iqr
        val highFence = q3 + 1.5 * iqr
        val inliers = sorted.filter { it >= lowFence && it <= highFence }
        val pool = if (inliers.size >= MIN_INLIER_SAMPLES) inliers else sorted

        val lo = pool.first().toDouble()
        val hi = pool.last().toDouble()
        val span = (hi - lo).coerceAtLeast(MIN_SPAN_YEARS) * PADDING_RATIO
        val center = (lo + hi) / 2.0
        val ppy = (1080.0 / span).toFloat().coerceIn(MIN_PPY, 3f)
        return AxisViewport(center, ppy)
    }

    /**
     * 视窗左右各能看到多少年。
     *
     * @param ppy 每年像素数。
     * @param canvasWidth 画布宽度（像素）。
     */
    fun halfSpanYears(ppy: Float, canvasWidth: Float): Double =
        (canvasWidth / 2.0) / ppy

    /**
     * 判断某年份是否落在视窗内（用于测试可见事件数）。
     */
    fun isVisible(year: Long, viewport: AxisViewport, canvasWidth: Float): Boolean {
        val half = halfSpanYears(viewport.pixelsPerYear, canvasWidth)
        return year.toDouble() in (viewport.centerYear - half)..(viewport.centerYear + half)
    }
}
