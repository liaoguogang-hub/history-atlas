package com.historyatlas.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextMeasurer
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.historyatlas.app.data.Event
import com.historyatlas.app.data.EventCategory
import com.historyatlas.app.data.Period
import com.historyatlas.app.ui.AxisViewport
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.colorFor
import kotlin.math.abs
import kotlin.math.floor

/**
 * 横向可缩放时间轴 —— 年表树的另一种视角。
 *
 * 布局（自上而下）：
 * ```
 * [朝代带]      时期色块 + 朝代名
 * [年代刻度]    每 100 年一格（随缩放自动加密/放疏）
 * [事件标记]    按重要度分层
 * [主轴 + 年份]
 * ```
 *
 * 交互：
 * - 双指捏合 → 缩放
 * - 单指拖动 → 平移（拖动方向与内容同向：向左拖，时间往后走）
 * - 单击标记 → 选中事件
 */

/** 年代刻度候选间隔（年）。100 年为主档，放大后逐级细化。 */
private val TickIntervals =
    listOf(1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000)

/** 事件分类 → 标记颜色。 */
private val AxisCategoryColors: Map<EventCategory, Color> = mapOf(
    EventCategory.POLITICAL to Color(0xFF3A5F9E),
    EventCategory.MILITARY to Color(0xFFA85252),
    EventCategory.CONFLICT to Color(0xFFB05540),
    EventCategory.ECONOMIC to Color(0xFF8F6A20),
    EventCategory.ECONOMY_CRISIS to Color(0xFF9A5B33),
    EventCategory.CULTURAL to Color(0xFF7A4C8C),
    EventCategory.LITERATURE to Color(0xFF85558F),
    EventCategory.ART to Color(0xFFA85178),
    EventCategory.SCIENTIFIC to Color(0xFF2F6F8F),
    EventCategory.TECHNOLOGY to Color(0xFF2F6F6A),
    EventCategory.EXPLORATION to Color(0xFF44754A),
    EventCategory.SOCIAL to Color(0xFF6B6B5F),
    EventCategory.EDUCATION to Color(0xFF5C7040),
    EventCategory.RELIGIOUS to Color(0xFF7A6247),
    EventCategory.HEALTH to Color(0xFF357068),
    EventCategory.TREATY to Color(0xFF4C6B5C),
    EventCategory.REFORM to Color(0xFF61509B),
    EventCategory.DYNASTY to Color(0xFF9E4A4A),
    EventCategory.CROSS_CIVILIZATION to Color(0xFF946A22),
    EventCategory.DISASTER to Color(0xFF7D5C4E),
)

private const val MIN_PPY = 0.0008f
private const val MAX_PPY = 400f

/** 年份 → 简短标签。 */
private fun yearLabel(y: Int): String = when {
    y < 0 -> "前${-y}"
    y == 0 -> "公元元年"
    else -> "$y"
}

/**
 * 时间轴画布。
 *
 * @param events 已在外部筛选过的事件。
 * @param periods 用于绘制朝代带的时期列表（可为空）。
 * @param viewport 外部持有的视窗状态；为 null 时按事件分布自动初始化。
 * @param onViewportChange 视窗变化回调，用于在返回本页时恢复位置。
 */
@Composable
fun TimelineAxis(
    events: List<Event>,
    modifier: Modifier = Modifier,
    periods: List<Period> = emptyList(),
    viewport: AxisViewport? = null,
    onViewportChange: (AxisViewport) -> Unit = {},
    onEventClick: (Event) -> Unit = {},
    selectedEventId: String? = null,
) {
    val measurer = rememberTextMeasurer()

    // 默认视窗：取事件年份的 2%~92% 分位，避开「前 170 万年」这类离群点，
    // 否则全部标记会挤成一条线。
    val defaultViewport = remember(events) {
        if (events.isEmpty()) {
            AxisViewport(0f, 0.5f)
        } else {
            val years = events.map { it.year }.sorted()
            fun q(p: Double): Float {
                val i = ((years.size - 1) * p).toInt().coerceIn(0, years.size - 1)
                return years[i].toFloat()
            }
            val lo = q(0.02)
            val hi = q(0.92)
            val span = (hi - lo).coerceAtLeast(1f)
            AxisViewport((lo + hi) / 2f, (1080f / span).coerceIn(MIN_PPY, 3f))
        }
    }

    var centerYear by remember { mutableFloatStateOf(viewport?.centerYear ?: defaultViewport.centerYear) }
    var pixelsPerYear by remember {
        mutableFloatStateOf(viewport?.pixelsPerYear ?: defaultViewport.pixelsPerYear)
    }

    // 外部视窗变化（例如从别的 scope 切回来）时同步进来
    androidx.compose.runtime.LaunchedEffect(viewport) {
        if (viewport != null) {
            centerYear = viewport.centerYear
            pixelsPerYear = viewport.pixelsPerYear
        }
    }

    var canvasWidth by remember { mutableFloatStateOf(1f) }

    fun pushViewport() = onViewportChange(AxisViewport(centerYear, pixelsPerYear))

    // 刻度间隔：让相邻刻度落在 70–160px 之间；100 年作为常用档位
    val tickInterval = remember(pixelsPerYear) {
        TickIntervals.firstOrNull { it * pixelsPerYear >= 70.0f } ?: TickIntervals.last()
    }

    fun yearToX(year: Float): Float =
        canvasWidth / 2f + (year - centerYear) * pixelsPerYear

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(320.dp)
            .background(Color(0xFFFCFAF6)),
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                // 点击手势必须先于缩放手势注册：两个 pointerInput 修饰符串联时，
                // 前面的会先拿到事件；若让 detectTransformGestures 在前，
                // 轻点会被拖动识别吃掉，点标记没有反应。
                // detectTapGestures 一旦检测到移动就会放弃，因此不影响拖动与缩放。
                .pointerInput(events) {
                    detectTapGestures { offset ->
                        val target = events.minByOrNull { e ->
                            abs(yearToX(e.year.toFloat()) - offset.x)
                        }
                        if (target != null &&
                            abs(yearToX(target.year.toFloat()) - offset.x) < 44f
                        ) {
                            onEventClick(target)
                        }
                    }
                }
                .pointerInput(Unit) {
                    detectTransformGestures { _, pan, zoom, _ ->
                        pixelsPerYear = (pixelsPerYear * zoom).coerceIn(MIN_PPY, MAX_PPY)
                        // 拖动方向与内容同向：手指向左滑 → 时间往后推进。
                        // 旧实现是 +=，与地图类应用的手感相反。
                        centerYear -= pan.x / pixelsPerYear
                        onViewportChange(AxisViewport(centerYear, pixelsPerYear))
                    }
                },
        ) {
            canvasWidth = size.width

            val bandH = 30.dp.toPx()          // 朝代带高度
            val axisY = size.height - 40.dp.toPx()   // 主轴位置
            val labelY = size.height - 26.dp.toPx()  // 年份标签基线

            // ---- 公元前底色 ----
            val bcLeft = yearToX(0f)
            if (bcLeft > 0) {
                drawRect(
                    color = Color(0xFFF3EFE6),
                    topLeft = Offset(0f, 0f),
                    size = Size(bcLeft, size.height),
                )
            }

            // ---- 朝代带：每个时期画一段色块 + 名称 ----
            if (periods.isNotEmpty()) {
                val viewLo = centerYear - size.width / 2f / pixelsPerYear
                val viewHi = centerYear + size.width / 2f / pixelsPerYear
                // 只画时间上属于「编年主干」的时期，区域专题会互相重叠
                val visible = periods
                    .filter { it.endYear >= viewLo && it.startYear <= viewHi }
                    .filter { it.parentId == null }
                    .sortedBy { it.startYear }

                clipRect(left = 0f, top = 0f, right = size.width, bottom = bandH) {
                    visible.forEach { p ->
                        val x1 = yearToX(p.startYear.toFloat()).coerceIn(-2000f, size.width + 2000f)
                        val x2 = yearToX(p.endYear.toFloat()).coerceIn(-2000f, size.width + 2000f)
                        val w = (x2 - x1).coerceAtLeast(1f)
                        if (x2 < 0 || x1 > size.width) return@forEach
                        val colors = colorFor(p.colorKey, p.id)
                        drawRect(
                            color = colors.block,
                            topLeft = Offset(x1, 4f),
                            size = Size(w, bandH - 8f),
                        )
                        drawLine(
                            color = colors.accent.copy(alpha = 0.35f),
                            start = Offset(x1, 4f),
                            end = Offset(x1, bandH - 4f),
                            strokeWidth = 1f,
                        )
                        // 名称：块宽度够时才画，避免糊成一团
                        if (w > 46f) {
                            val layout = measurer.measure(
                                text = p.name,
                                style = TextStyle(
                                    fontSize = 10.sp,
                                    color = colors.accent,
                                    fontWeight = FontWeight.Medium,
                                ),
                                maxLines = 1,
                            )
                            val tx = (x1 + 5f).coerceIn(2f, size.width - layout.size.width - 2f)
                            drawText(layout, topLeft = Offset(tx, 10f))
                        }
                    }
                }
            }

            // ---- 年代竖网格线 ----
            // 100 年一格作为基准网格（缩放到够宽时才画），
            // 主刻度另按 tickInterval 走，保证任何缩放级别下都能读出「世纪」。
            val minorStep = 100
            if (minorStep * pixelsPerYear >= 6f) {
                val f0 = floor((centerYear - size.width / pixelsPerYear) / minorStep).toInt() - 1
                val l0 = (centerYear + size.width / pixelsPerYear).toInt() / minorStep + 1
                for (g in f0..l0) {
                    val x = yearToX((g * minorStep).toFloat())
                    if (x < -20 || x > size.width + 20) continue
                    drawLine(
                        color = Color(0xFFF1ECE2),
                        start = Offset(x, bandH),
                        end = Offset(x, axisY),
                        strokeWidth = 0.7f,
                    )
                }
            }

            val gridStep = tickInterval
            val firstGrid = floor((centerYear - size.width / pixelsPerYear) / gridStep).toInt() - 1
            val lastGrid = (centerYear + size.width / pixelsPerYear).toInt() / gridStep + 1
            for (g in firstGrid..lastGrid) {
                val x = yearToX((g * gridStep).toFloat())
                if (x < -20 || x > size.width + 20) continue
                drawLine(
                    color = Color(0xFFE2DACB),
                    start = Offset(x, bandH),
                    end = Offset(x, axisY),
                    strokeWidth = 1.2f,
                )
            }

            // ---- 公元零线 ----
            drawLine(
                color = Color(0xFFC0A97F),
                start = Offset(bcLeft, bandH),
                end = Offset(bcLeft, size.height),
                strokeWidth = 2f,
            )

            // ---- 事件标记 ----
            val usableHeight = axisY - bandH - 8f
            events.forEach { e ->
                val x = yearToX(e.year.toFloat())
                if (x < -40 || x > size.width + 40) return@forEach
                val cat = EventCategory.from(e.category)
                val color = AxisCategoryColors[cat] ?: Color(0xFF6B6B5F)
                val isSelected = e.id == selectedEventId
                val radius = when (e.importance) {
                    5 -> 6.5f
                    4 -> 5.2f
                    3 -> 4.2f
                    2 -> 3.4f
                    else -> 2.8f
                }
                val tier = (e.importance.coerceIn(1, 5) - 1)
                val markY = axisY - usableHeight * (0.12f + tier * 0.17f)

                if (e.yearEnd != null && e.yearEnd > e.year) {
                    val xEnd = yearToX(e.yearEnd.toFloat())
                    drawLine(
                        color = color.copy(alpha = 0.4f),
                        start = Offset(x, markY),
                        end = Offset(xEnd.coerceAtLeast(x), markY),
                        strokeWidth = if (isSelected) 6f else 3f,
                    )
                }

                drawLine(
                    color = color.copy(alpha = 0.28f),
                    start = Offset(x, axisY),
                    end = Offset(x, markY),
                    strokeWidth = if (isSelected) 2.5f else 1f,
                )
                drawCircle(
                    color = color,
                    radius = if (isSelected) radius + 2.5f else radius,
                    center = Offset(x, markY),
                )
                if (isSelected) {
                    drawCircle(
                        color = color.copy(alpha = 0.3f),
                        radius = radius + 6f,
                        center = Offset(x, markY),
                    )
                }
            }

            // ---- 主轴 ----
            drawLine(
                color = Color(0xFFB9AF9C),
                start = Offset(0f, axisY),
                end = Offset(size.width, axisY),
                strokeWidth = 2f,
            )

            // ---- 年份标签（每格一个，100 年为主档） ----
            val firstTick = floor((centerYear - size.width / pixelsPerYear) / tickInterval).toInt() - 1
            val lastTick = (centerYear + size.width / pixelsPerYear).toInt() / tickInterval + 1
            var lastLabelRight = -1000f
            for (t in firstTick..lastTick) {
                val year = t * tickInterval
                val x = yearToX(year.toFloat())
                if (x < -60 || x > size.width + 60) continue
                drawLine(
                    color = Color(0xFFCFC6B8),
                    start = Offset(x, axisY),
                    end = Offset(x, axisY + 6f),
                    strokeWidth = 1.4f,
                )
                val layout = measurer.measure(
                    text = yearLabel(year),
                    style = TextStyle(fontSize = 9.sp, color = InkTertiary),
                    maxLines = 1,
                )
                val tx = x - layout.size.width / 2f
                // 标签互相重叠时跳过，保证可读
                if (tx < lastLabelRight + 4f) continue
                if (tx < -layout.size.width || tx > size.width) continue
                drawText(layout, topLeft = Offset(tx, labelY))
                lastLabelRight = tx + layout.size.width
            }
        }
    }
}

/**
 * 事件在时间轴上的紧凑标记标签（用于选中事件的浮层）。
 */
@Composable
fun EventAxisChip(
    event: Event,
    modifier: Modifier = Modifier,
) {
    val cat = EventCategory.from(event.category)
    val color = AxisCategoryColors[cat] ?: Color(0xFF6B6B5F)
    Row(
        modifier = modifier
            .background(Color.White, RoundedCornerShape(8.dp))
            .padding(horizontal = 10.dp, vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(8.dp)
                .background(color, CircleShape),
        )
        Spacer(Modifier.width(7.dp))
        Column {
            Text(
                text = event.name,
                color = InkPrimary,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
            )
            Text(
                text = "${event.dateText} · ${cat.label}",
                color = InkTertiary,
                fontSize = 10.sp,
            )
        }
    }
}
