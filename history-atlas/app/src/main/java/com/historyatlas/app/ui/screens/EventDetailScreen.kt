package com.historyatlas.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.historyatlas.app.data.Event
import com.historyatlas.app.data.EventCategory
import com.historyatlas.app.data.Figure
import com.historyatlas.app.data.HistoryRepository
import com.historyatlas.app.data.Period
import com.historyatlas.app.ui.components.AtlasCard
import com.historyatlas.app.ui.components.CategoryBadge
import com.historyatlas.app.ui.components.EmptyHint
import com.historyatlas.app.ui.components.FigureAvatar
import com.historyatlas.app.ui.components.ImportanceStars
import com.historyatlas.app.ui.components.SectionHeader
import com.historyatlas.app.ui.theme.CardSurface
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.OutlineSoft
import com.historyatlas.app.ui.theme.Paper

/**
 * 事件详情页。
 *
 * 结构：元信息条 → 标题 → 摘要 → 正文（可折叠）→ 涉及人物 → 相关事件。
 */
@Composable
fun EventDetailScreen(
    repository: HistoryRepository,
    eventId: String,
    scope: String,
    onBack: () -> Unit,
    onFigureClick: (Figure) -> Unit,
    onEventClick: (Event) -> Unit,
    onPeriodClick: (Period) -> Unit,
) {
    val event = remember(eventId, scope) { repository.event(eventId, scope) }

    if (event == null) {
        Scaffold(containerColor = Paper, topBar = { DetailTopBar("事件不存在", onBack) }) { padding ->
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                EmptyHint("未找到该事件")
            }
        }
        return
    }

    val figures = remember(eventId, scope) { repository.resolveFigureIds(event.figures, scope) }
    val period = remember(eventId, scope) { repository.period(event.periodId, scope) }
    val related = remember(eventId, scope) {
        val all = repository.eventsOf(event.periodId, scope)
        val sameCat = all.filter { it.category == event.category && it.id != event.id }
        val sharedFigures = all.filter {
            it.id != event.id && it.figures.any { f -> event.figures.contains(f) }
        }
        (sameCat + sharedFigures).distinctBy { it.id }.take(8)
    }

    var expanded by remember { mutableStateOf(false) }
    val detailText = event.detail
    val shouldTruncate = detailText.length > 220
    val visibleText = if (expanded || !shouldTruncate) detailText else detailText.take(220)

    Scaffold(
        containerColor = Paper,
        topBar = { DetailTopBar(event.dateText.ifBlank { "事件" }, onBack) },
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // ---- 元信息 ----
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CategoryBadge(EventCategory.from(event.category))
                    Spacer(Modifier.width(8.dp))
                    ImportanceStars(event.importance)
                    Spacer(Modifier.weight(1f))
                    if (event.location.isNotBlank()) {
                        Icon(
                            imageVector = Icons.Outlined.LocationOn,
                            contentDescription = null,
                            tint = InkTertiary,
                            modifier = Modifier.size(13.dp),
                        )
                        Spacer(Modifier.width(2.dp))
                        Text(
                            text = event.location,
                            color = InkTertiary,
                            fontSize = 11.sp,
                        )
                    }
                }
            }

            // ---- 标题 ----
            item {
                Text(
                    text = event.name,
                    color = InkPrimary,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 31.sp,
                    modifier = Modifier.padding(horizontal = 16.dp),
                )
            }

            // ---- 所属时期 ----
            if (period != null) {
                item {
                    Row(
                        modifier = Modifier
                            .padding(horizontal = 16.dp)
                            .background(Color(0xFFF0EBE1), RoundedCornerShape(12.dp))
                            .clickable { onPeriodClick(period) }
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "所属时期",
                            color = InkTertiary,
                            fontSize = 11.sp,
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = period.name,
                            color = MaterialTheme.colorScheme.primary,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = period.yearRangeText,
                            color = InkTertiary,
                            fontSize = 10.sp,
                        )
                    }
                }
            }

            // ---- 摘要 ----
            if (event.summary.isNotBlank()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Text(
                                text = event.summary,
                                color = InkSecondary,
                                fontSize = 14.sp,
                                lineHeight = 24.sp,
                            )
                        }
                    }
                }
            }

            // ---- 正文 ----
            if (detailText.isNotBlank()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Column {
                                SectionHeader("详细记述")
                                Spacer(Modifier.height(8.dp))
                                Text(
                                    text = visibleText,
                                    color = InkSecondary,
                                    fontSize = 14.sp,
                                    lineHeight = 25.sp,
                                )
                                if (shouldTruncate) {
                                    Spacer(Modifier.height(8.dp))
                                    Text(
                                        text = if (expanded) "收起" else "展开全文",
                                        color = MaterialTheme.colorScheme.primary,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        modifier = Modifier.clickable { expanded = !expanded },
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // ---- 涉及人物 ----
            if (figures.isNotEmpty()) {
                item {
                    Column {
                        Box(Modifier.padding(horizontal = 14.dp)) {
                            SectionHeader("涉及人物", trailing = "${figures.size} 位")
                        }
                        Spacer(Modifier.height(8.dp))
                        LazyRow(
                            contentPadding = PaddingValues(horizontal = 14.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            items(figures, key = { it.id }) { figure ->
                                FigureChip(figure, onClick = { onFigureClick(figure) })
                            }
                        }
                    }
                }
            }

            // ---- 相关事件 ----
            if (related.isNotEmpty()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        SectionHeader("相关事件")
                    }
                }
                items(related, key = { it.id }) { rel ->
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        EventRow(rel, onClick = { onEventClick(rel) })
                    }
                }
            }

            // ---- 标签 ----
            if (event.tags.isNotEmpty()) {
                item {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        event.tags.take(10).forEach { tag ->
                            com.historyatlas.app.ui.components.TagChip(tag)
                        }
                    }
                }
            }
        }
    }
}
