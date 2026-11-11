package com.scienceatlas.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.EventCategory
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft

/**
 * 通用 UI 组件库。
 */

// ---------------------------------------------------------------------------
// 分类徽章
// ---------------------------------------------------------------------------

/** 事件分类 → 徽章底色 / 文字色。 */
private val CategoryColors: Map<EventCategory, Pair<Color, Color>> = mapOf(
    EventCategory.SCIENTIFIC to (Color(0xFFDDE7F5) to Color(0xFF2F5B96)),
    EventCategory.TECHNOLOGY to (Color(0xFFD9EDE8) to Color(0xFF2E6E66)),
    EventCategory.EXPLORATION to (Color(0xFFE2EEE3) to Color(0xFF44754A)),
    EventCategory.REFORM to (Color(0xFFEAE4F5) to Color(0xFF61509B)),
    EventCategory.CULTURAL to (Color(0xFFEDE3F3) to Color(0xFF7A4C8C)),
    EventCategory.LITERATURE to (Color(0xFFF1E6F2) to Color(0xFF85558F)),
    EventCategory.ART to (Color(0xFFF9E7EF) to Color(0xFFA85178)),
    EventCategory.ECONOMIC to (Color(0xFFF6ECD8) to Color(0xFF8F6A20)),
    EventCategory.ECONOMY_CRISIS to (Color(0xFFF3E2D6) to Color(0xFF9A5B33)),
    EventCategory.HEALTH to (Color(0xFFDFEFEC) to Color(0xFF357068)),
    EventCategory.EDUCATION to (Color(0xFFE8EDE2) to Color(0xFF5C7040)),
    EventCategory.TREATY to (Color(0xFFE4EAE6) to Color(0xFF4C6B5C)),
    EventCategory.POLITICAL to (Color(0xFFE3EAF6) to Color(0xFF3A5F9E)),
    EventCategory.MILITARY to (Color(0xFFF7DEDE) to Color(0xFFA85252)),
    EventCategory.CONFLICT to (Color(0xFFFAE3DC) to Color(0xFFB05540)),
    EventCategory.SOCIAL to (Color(0xFFE9E9E4) to Color(0xFF6B6B5F)),
    EventCategory.RELIGIOUS to (Color(0xFFEDE6DA) to Color(0xFF7A6247)),
    EventCategory.DYNASTY to (Color(0xFFF6E3E3) to Color(0xFF9E4A4A)),
    EventCategory.CROSS_CIVILIZATION to (Color(0xFFF5EBD6) to Color(0xFF946A22)),
    EventCategory.DISASTER to (Color(0xFFE8E3E0) to Color(0xFF7D5C4E)),
    EventCategory.LEGEND to (Color(0xFFEDE6F2) to Color(0xFF6E5C8A)),
    EventCategory.ARCHAEOLOGY to (Color(0xFFE9E5DA) to Color(0xFF6E6548)),
)

/**
 * 事件分类徽章。
 *
 * @param category 分类枚举值。
 * @param compact 紧凑模式：只显示圆点，不显示文字（用于列表右侧）。
 */
@Composable
fun CategoryBadge(
    category: EventCategory,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    val (bg, fg) = CategoryColors[category] ?: (Color(0xFFE9E9E4) to InkSecondary)
    if (compact) {
        Box(
            modifier = modifier
                .size(8.dp)
                .background(fg.copy(alpha = 0.75f), CircleShape),
        )
        return
    }
    Box(
        modifier = modifier
            .background(bg, RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp),
    ) {
        Text(
            text = category.label,
            color = fg,
            fontSize = 11.sp,
            fontWeight = FontWeight.Medium,
        )
    }
}

// ---------------------------------------------------------------------------
// 重要度星级
// ---------------------------------------------------------------------------

/**
 * 重要度星级。
 *
 * @param importance 1..5。
 * @param compact 只画点不画星（空间不足时）。
 */
@Composable
fun ImportanceStars(
    importance: Int,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(1.dp),
    ) {
        val filled = importance.coerceIn(0, 5)
        repeat(5) { index ->
            val on = index < filled
            Text(
                text = if (on) "★" else "☆",
                color = if (on) Color(0xFFD9A441) else OutlineSoft,
                fontSize = if (compact) 10.sp else 13.sp,
            )
        }
    }
}

// ---------------------------------------------------------------------------
// 人物头像
// ---------------------------------------------------------------------------

/** 身份关键词 → 头像底色。 */
private val RolePalette: List<Color> = listOf(
    Color(0xFFDDE9F0), Color(0xFFF3E2D8), Color(0xFFE2EEE3),
    Color(0xFFEDE3F3), Color(0xFFF6ECD8), Color(0xFFE8E9E4),
)

/**
 * 圆形人物头像：以姓名首字为内容，按身份着色。
 *
 * @param name 人物姓名。
 * @param role 身份，用于决定底色。
 * @param size 直径。
 */
@Composable
fun FigureAvatar(
    name: String,
    role: String = "",
    modifier: Modifier = Modifier,
    size: Int = 44,
) {
    val hash = (name + role).fold(0) { acc, ch -> (acc * 31 + ch.code) and 0x7FFFFFFF }
    val bg = RolePalette[hash % RolePalette.size]
    val initial = name.trim().firstOrNull()?.toString() ?: "?"
    Box(
        modifier = modifier
            .size(size.dp)
            .background(bg, CircleShape)
            .border(1.dp, OutlineSoft.copy(alpha = 0.6f), CircleShape),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = initial,
            color = InkPrimary.copy(alpha = 0.72f),
            fontSize = (size * 0.42f).sp,
            fontWeight = FontWeight.Medium,
        )
    }
}

// ---------------------------------------------------------------------------
// 分区标题
// ---------------------------------------------------------------------------

/** 分区标题，带左侧竖线装饰。 */
@Composable
fun SectionHeader(
    title: String,
    modifier: Modifier = Modifier,
    trailing: String? = null,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .width(3.dp)
                .height(15.dp)
                .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.75f), RoundedCornerShape(2.dp)),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = InkPrimary,
        )
        if (trailing != null) {
            Spacer(Modifier.width(8.dp))
            Text(
                text = trailing,
                style = MaterialTheme.typography.labelSmall,
                color = InkTertiary,
            )
        }
    }
}

// ---------------------------------------------------------------------------
// 概况行
// ---------------------------------------------------------------------------

/**
 * 概况行：图标 + 标签 + 值。
 *
 * @param icon 字段图标，可为空。
 */
@Composable
fun InfoRow(
    icon: ImageVector?,
    label: String,
    value: String,
    modifier: Modifier = Modifier,
) {
    if (value.isBlank()) return
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        verticalAlignment = Alignment.Top,
    ) {
        if (icon != null) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.8f),
                modifier = Modifier.size(16.dp),
            )
            Spacer(Modifier.width(8.dp))
        }
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = InkTertiary,
            modifier = Modifier.width(56.dp),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = InkSecondary,
            modifier = Modifier.weight(1f),
        )
    }
}

// ---------------------------------------------------------------------------
// 名言引用卡
// ---------------------------------------------------------------------------

/** 名言引用卡：左侧竖线 + 引文。 */
@Composable
fun QuoteCard(
    quote: String,
    modifier: Modifier = Modifier,
    attribution: String? = null,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(Color(0xFFF1F4F9), RoundedCornerShape(8.dp))
            .padding(12.dp),
    ) {
        Box(
            Modifier
                .width(3.dp)
                .height(if (attribution == null) 34.dp else 48.dp)
                .background(Color(0xFF9FB0CC), RoundedCornerShape(2.dp)),
        )
        Spacer(Modifier.width(12.dp))
        Column {
            Text(
                text = "「$quote」",
                style = MaterialTheme.typography.bodyMedium,
                color = InkPrimary.copy(alpha = 0.9f),
                lineHeight = 22.sp,
            )
            if (attribution != null) {
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "— $attribution",
                    style = MaterialTheme.typography.labelSmall,
                    color = InkTertiary,
                )
            }
        }
    }
}

// ---------------------------------------------------------------------------
// 高亮文本
// ---------------------------------------------------------------------------

/**
 * 在文本中高亮命中的关键词。
 *
 * @param text 原始文本。
 * @param query 搜索词，为空时原样返回。
 */
@Composable
fun HighlightedText(
    text: String,
    query: String,
    modifier: Modifier = Modifier,
    style: TextStyle = MaterialTheme.typography.bodyMedium,
    maxLines: Int = Int.MAX_VALUE,
    color: Color = InkPrimary,
) {
    val annotated = remember(text, query) { buildHighlighted(text, query) }
    Text(
        text = annotated,
        style = style,
        color = color,
        maxLines = maxLines,
        overflow = TextOverflow.Ellipsis,
        modifier = modifier,
    )
}

private fun buildHighlighted(text: String, query: String): androidx.compose.ui.text.AnnotatedString {
    val q = query.trim()
    if (q.isEmpty() || text.isEmpty()) return buildAnnotatedString { append(text) }
    val lower = text.lowercase()
    val needle = q.lowercase()
    return buildAnnotatedString {
        var index = 0
        while (index < text.length) {
            val hit = lower.indexOf(needle, index)
            if (hit < 0) {
                append(text.substring(index))
                break
            }
            if (hit > index) append(text.substring(index, hit))
            withStyle(
                SpanStyle(
                    color = Color(0xFF1F4F8F),
                    fontWeight = FontWeight.SemiBold,
                    background = Color(0xFFDCE7F8),
                ),
            ) {
                append(text.substring(hit, hit + needle.length))
            }
            index = hit + needle.length
        }
    }
}

// ---------------------------------------------------------------------------
// 标签芯片
// ---------------------------------------------------------------------------

/** 静态标签（不可点）。 */
@Composable
fun TagChip(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Color(0xFFE7ECF3),
    textColor: Color = InkSecondary,
) {
    Box(
        modifier = modifier
            .background(color, RoundedCornerShape(5.dp))
            .padding(horizontal = 7.dp, vertical = 2.dp),
    ) {
        Text(
            text = text,
            fontSize = 11.sp,
            color = textColor,
            maxLines = 1,
        )
    }
}

/** 可点筛选芯片。 */
@Composable
fun FilterChip(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val bg = if (selected) MaterialTheme.colorScheme.primary else Color(0xFFEFF2F7)
    val fg = if (selected) Color.White else InkSecondary
    Box(
        modifier = modifier
            .background(bg, RoundedCornerShape(14.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 6.dp),
    ) {
        Text(text = text, fontSize = 12.sp, color = fg)
    }
}

// ---------------------------------------------------------------------------
// 通用卡片
// ---------------------------------------------------------------------------

/** 内容卡片：白底 + 细边框 + 圆角。 */
@Composable
fun AtlasCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    content: @Composable () -> Unit,
) {
    val shape = RoundedCornerShape(12.dp)
    Card(
        modifier = modifier.then(
            if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier,
        ),
        shape = shape,
        colors = CardDefaults.cardColors(containerColor = CardSurface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, OutlineSoft),
    ) {
        Box(Modifier.padding(14.dp)) { content() }
    }
}

/** 空态占位。 */
@Composable
fun EmptyHint(
    text: String,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 28.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = InkTertiary,
        )
    }
}

/**
 * 轻量搜索框：用于时间轴、人物志、事件流等列表页顶部。
 *
 * 与独立的搜索页不同，这里只做当前页面的就地过滤，
 * 因此样式更紧凑，且带清空按钮。
 */
@Composable
fun AtlasSearchField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(40.dp)
            .background(CardSurface, RoundedCornerShape(10.dp))
            .border(1.dp, OutlineSoft, RoundedCornerShape(10.dp))
            .padding(horizontal = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Outlined.Search,
            contentDescription = null,
            tint = InkTertiary,
            modifier = Modifier.size(16.dp),
        )
        Spacer(Modifier.width(7.dp))
        Box(Modifier.weight(1f), contentAlignment = Alignment.CenterStart) {
            if (value.isEmpty()) {
                Text(
                    text = placeholder,
                    color = InkTertiary,
                    fontSize = 13.sp,
                )
            }
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                singleLine = true,
                textStyle = TextStyle(
                    color = InkPrimary,
                    fontSize = 13.sp,
                ),
                cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                modifier = Modifier.fillMaxWidth(),
            )
        }
        if (value.isNotEmpty()) {
            IconButton(
                onClick = { onValueChange("") },
                modifier = Modifier.size(24.dp),
            ) {
                Icon(
                    imageVector = Icons.Filled.Close,
                    contentDescription = "清空",
                    tint = InkTertiary,
                    modifier = Modifier.size(15.dp),
                )
            }
        }
    }
}
