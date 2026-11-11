package com.scienceatlas.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.colorFor
import kotlin.math.sqrt

/**
 * 分期年表树的色块 —— 本 App 视觉语言的核心构件。
 *
 * 布局：
 * - 圆角色块，浅马卡龙底色
 * - 左上角标题（深墨色、粗体）
 * - 下方起止年份（次级色、小字）
 * - 高度按持续年数的**平方根**映射，短分期也能读，长分期不过分膨胀
 */

/** 色块高度区间（dp）。 */
private val MinBlockHeight = 62.dp
private val MaxBlockHeight = 158.dp

/**
 * 计算色块高度。
 *
 * 用平方根而非线性：线性映射会让短分期压成一条线，
 * 平方根能在保持长分期相对差异的同时给短分期留出可读高度。
 *
 * @param span 持续年数。
 * @param maxSpan 全部节点中的最大跨度，作为归一化基准。
 */
private fun blockHeight(span: Long, maxSpan: Long): androidx.compose.ui.unit.Dp {
    if (maxSpan <= 0) return MinBlockHeight
    val ratio = (sqrt(span.coerceAtLeast(1L).toDouble()) / sqrt(maxSpan.toDouble())).toFloat()
    val minPx = MinBlockHeight.value
    val maxPx = MaxBlockHeight.value
    return (minPx + (maxPx - minPx) * ratio).coerceIn(minPx, maxPx).dp
}

/**
 * 紧凑日期文本：把 `公元前300万年` 压成 `前300万年`，`公元220年` 压成 `220年`。
 *
 * 色块宽度有限（尤其三级节点），完整前缀会导致省略号。
 * 这里只去掉「公元」二字，保留「前」以区分公元前 —— 这是不可省略的语义。
 */
internal fun compactDate(text: String): String = when {
    text.startsWith("公元前") -> "前" + text.removePrefix("公元前")
    text.startsWith("公元") -> text.removePrefix("公元")
    else -> text
}

/**
 * 时期起始年的极简刻度标签，供脊柱中点使用。
 *
 * 脊柱宽度 46dp，`前1046年` 之类放不下完整年月表述，这里只留数字与「前」标记。
 * 史前时期的绝对值可达百万级（如 -3000000 会写成八字的「前3000000」，
 * 必然溢出），因此一万以上改用「万」为单位并保留一位小数。
 *
 * 地质深时的数值更大（-4600000000），「万」为单位也不够用，
 * 因此再大一档改用「亿」。
 */
internal fun Period.startYearLabel(): String {
    val y = startYear
    val mag = kotlin.math.abs(y)
    val num = when {
        mag >= 100_000_000L -> {
            val yi = mag / 100_000_000.0
            val text = if (yi >= 10.0) {
                "%.0f亿".format(yi)
            } else {
                val one = "%.1f".format(yi)
                (if (one.endsWith(".0")) one.dropLast(2) else one) + "亿"
            }
            text
        }
        mag >= 10000L -> {
            val wan = mag / 10000.0
            val text = if (wan >= 10.0) {
                // 十万以上不再保留小数，避免「前300.0万」这类冗长写法
                "%.0f万".format(wan)
            } else {
                val one = "%.1f".format(wan)
                (if (one.endsWith(".0")) one.dropLast(2) else one) + "万"
            }
            text
        }
        else -> "${mag}"
    }
    return if (y < 0) "前${num}" else num
}

/**
 * 分期色块。
 *
 * @param period 分期数据。
 * @param maxSpan 该 scope 内最大时间跨度，用于高度归一化。
 * @param onClick 点击回调。
 * @param highlight 是否高亮（搜索命中）。
 */
@Composable
fun PeriodBlock(
    period: Period,
    maxSpan: Long,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    highlight: Boolean = false,
    height: androidx.compose.ui.unit.Dp? = null,
) {
    val colors = colorFor(period.colorKey, period.id)
    val boxHeight = height ?: blockHeight((period.endYear - period.startYear).coerceAtLeast(0L), maxSpan)

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(boxHeight)
            .clip(RoundedCornerShape(7.dp))
            .background(colors.block)
            .then(
                if (highlight) {
                    Modifier.border(2.dp, MaterialTheme.colorScheme.primary, RoundedCornerShape(7.dp))
                } else {
                    Modifier.border(0.5.dp, colors.accent.copy(alpha = 0.16f), RoundedCornerShape(7.dp))
                },
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 6.dp),
    ) {
        Column {
            Text(
                text = period.name,
                color = colors.accent,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                lineHeight = 18.sp,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(Modifier.height(2.dp))
            // 起止年份合并为一行，避免短分期块高度不足时第二行被裁掉。
            Text(
                text = "${compactDate(period.startDateText)} – ${compactDate(period.endDateText)}",
                color = InkSecondary.copy(alpha = 0.78f),
                fontSize = 9.sp,
                lineHeight = 12.sp,
                maxLines = 2,
                overflow = TextOverflow.Visible,
            )
        }
    }
}

/**
 * 左侧「阶段」脊柱块。
 *
 * @param height 脊柱块高度；传入该阶段所有子块的总高可使左右两列行对齐。
 */
@Composable
fun EraSpineBlock(
    period: Period,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    height: androidx.compose.ui.unit.Dp = 56.dp,
) {
    val colors = colorFor(period.colorKey, period.id)
    Box(
        modifier = modifier
            .width(78.dp)
            .height(height)
            .clip(RoundedCornerShape(7.dp))
            .background(colors.block)
            .border(0.5.dp, colors.accent.copy(alpha = 0.2f), RoundedCornerShape(7.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 6.dp, vertical = 7.dp),
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = period.name,
                color = colors.accent,
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp,
                lineHeight = 17.sp,
                textAlign = TextAlign.Center,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(Modifier.height(3.dp))
            Text(
                text = "${compactDate(period.startDateText)}\n${compactDate(period.endDateText)}",
                color = InkTertiary,
                fontSize = 9.sp,
                lineHeight = 12.sp,
                textAlign = TextAlign.Center,
                maxLines = 2,
            )
        }
    }
}

/**
 * 脊柱连接线：贯穿某个阶段所有子块高度的竖线 + 中点刻度。
 *
 * @param height 该阶段子块的总高度。
 * @param label 刻度标签（通常是年份）。
 */
@Composable
fun SpineConnector(
    height: androidx.compose.ui.unit.Dp,
    label: String,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .width(46.dp)
            .height(height),
    ) {
        // 竖线：靠左，给右侧刻度标签留出空间，避免文字被线穿过。
        Box(
            Modifier
                .align(Alignment.CenterStart)
                .padding(start = 5.dp)
                .width(1.5.dp)
                .fillMaxHeight()
                .background(Color(0xFFC3CBD8)),
        )
        // 中点刻度 + 标签
        Column(
            modifier = Modifier
                .align(Alignment.Center)
                .padding(start = 11.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                Modifier
                    .width(10.dp)
                    .height(1.5.dp)
                    .background(Color(0xFFC3CBD8)),
            )
            Text(
                text = label,
                color = InkTertiary,
                fontSize = 9.sp,
                maxLines = 1,
                softWrap = false,
                // 年份标签较长（如「前300万年」），缩放以避免被右侧色块裁切
                overflow = TextOverflow.Visible,
                textAlign = TextAlign.Start,
                modifier = Modifier.widthIn(min = 34.dp),
            )
        }
    }
}

/**
 * 三级年表块：一个阶段下的第二层与第三层。
 *
 * 结构：
 * ```
 * [阶段块] ─┬─ [子分期块]
 *           │  └─ [孙分期块]
 *           └─ [子分期块]
 * ```
 */
@Composable
fun PeriodGroup(
    era: Period,
    children: List<Period>,
    grandChildren: Map<String, List<Period>>,
    maxSpan: Long,
    onPeriodClick: (Period) -> Unit,
    modifier: Modifier = Modifier,
    highlightIds: Set<String> = emptySet(),
) {
    if (children.isEmpty()) {
        // 顶层没有子分期：只渲染一块满宽的分期块。
        val ownHeight = blockHeight((era.endYear - era.startYear).coerceAtLeast(0L), maxSpan)
        val colors = colorFor(era.colorKey, era.id)
        Row(
            modifier = modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            // 左侧细色条保留「阶段」的视觉锚点，但不重复文字
            Box(
                Modifier
                    .width(6.dp)
                    .height(ownHeight)
                    .clip(RoundedCornerShape(3.dp))
                    .background(colors.accent.copy(alpha = 0.35f)),
            )
            Spacer(Modifier.width(8.dp))
            PeriodBlock(
                period = era,
                maxSpan = maxSpan,
                onClick = { onPeriodClick(era) },
                highlight = era.id in highlightIds,
                modifier = Modifier.weight(1f),
            )
        }
        return
    }

    // 右侧 Column 是扁平排列：[子块, 孙块分组, 子块, 孙块分组 …]，
    // 由 spacedBy(4.dp) 在**每个相邻元素**之间插入间距。
    // 因此总高 = 所有子块高 + 所有孙块分组高 + 4dp × (元素数 - 1)。
    val innerGap = 4
    val grandGap = 3
    var itemCount = 0
    var columnHeight = 0.0
    children.forEach { child ->
        columnHeight += blockHeight(
            (child.endYear - child.startYear).coerceAtLeast(0L), maxSpan,
        ).value.toDouble()
        itemCount++
        val grands = grandChildren[child.id].orEmpty()
        if (grands.isNotEmpty()) {
            columnHeight += grands.fold(0.0) { acc, g ->
                acc + blockHeight((g.endYear - g.startYear).coerceAtLeast(0L), maxSpan)
                    .value.toDouble()
            }
            columnHeight += (grands.size - 1).coerceAtLeast(0) * grandGap
            itemCount++
        }
    }
    columnHeight += (itemCount - 1).coerceAtLeast(0) * innerGap
    val columnHeightDp = columnHeight.dp

    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top,
    ) {
        EraSpineBlock(
            period = era,
            onClick = { onPeriodClick(era) },
            height = columnHeightDp,
        )
        Spacer(Modifier.width(8.dp))
        SpineConnector(
            height = columnHeightDp,
            label = era.startYearLabel(),
        )
        Spacer(Modifier.width(4.dp))
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(innerGap.dp),
        ) {
            children.forEach { child ->
                PeriodBlock(
                    period = child,
                    maxSpan = maxSpan,
                    onClick = { onPeriodClick(child) },
                    highlight = child.id in highlightIds,
                )
                val grands = grandChildren[child.id].orEmpty()
                if (grands.isNotEmpty()) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(start = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(grandGap.dp),
                    ) {
                        grands.forEach { g ->
                            PeriodBlock(
                                period = g,
                                maxSpan = maxSpan,
                                onClick = { onPeriodClick(g) },
                                highlight = g.id in highlightIds,
                            )
                        }
                    }
                }
            }
        }
    }
}
