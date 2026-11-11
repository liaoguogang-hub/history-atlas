package com.scienceatlas.app.ui.screens

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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.outlined.Badge
import androidx.compose.material.icons.outlined.Groups
import androidx.compose.material.icons.outlined.Landscape
import androidx.compose.material.icons.outlined.LocationCity
import androidx.compose.material.icons.outlined.Science
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Event
import com.scienceatlas.app.data.EventCategory
import com.scienceatlas.app.data.Figure
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.components.AtlasCard
import com.scienceatlas.app.ui.components.CategoryBadge
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.FigureAvatar
import com.scienceatlas.app.ui.components.ImportanceStars
import com.scienceatlas.app.ui.components.InfoRow
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft
import com.scienceatlas.app.ui.theme.Paper
import com.scienceatlas.app.ui.theme.colorFor

/**
 * 分期详情页。
 *
 * 结构：色块 banner → 概况 → 概述 → 子分期 → 关键人物 → 代表事件。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PeriodDetailScreen(
    repository: ScienceRepository,
    periodId: String,
    scope: String,
    onBack: () -> Unit,
    onEventClick: (Event) -> Unit,
    onFigureClick: (Figure) -> Unit,
    onChildPeriodClick: (Period) -> Unit,
) {
    val period = remember(periodId, scope) { repository.period(periodId, scope) }

    if (period == null) {
        Scaffold(containerColor = Paper, topBar = { DetailTopBar("分期不存在", onBack) }) { padding ->
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                EmptyHint("未找到该分期")
            }
        }
        return
    }

    val children = remember(periodId, scope) { repository.childrenOf(periodId, scope) }
    val events = remember(periodId, scope) { repository.eventsOfSubtree(periodId, scope) }
    val figures = remember(periodId, scope) {
        repository.resolveFigureIds(period.keyFigures, scope)
    }
    val colors = colorFor(period.colorKey, period.id)

    Scaffold(
        containerColor = Paper,
        topBar = { DetailTopBar(period.name, onBack) },
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // ---- Banner ----
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(colors.block)
                        .padding(20.dp),
                ) {
                    Column {
                        if (period.alias.isNotBlank()) {
                            Text(
                                text = period.alias,
                                color = colors.accent.copy(alpha = 0.75f),
                                fontSize = 12.sp,
                            )
                        }
                        Text(
                            text = period.name,
                            color = colors.accent,
                            fontSize = 30.sp,
                            fontWeight = FontWeight.Bold,
                        )
                        Spacer(Modifier.height(6.dp))
                        Text(
                            text = period.yearRangeText,
                            color = InkSecondary.copy(alpha = 0.85f),
                            fontSize = 14.sp,
                        )
                    }
                }
            }

            // ---- 概况 ----
            item {
                Box(Modifier.padding(horizontal = 14.dp)) {
                    AtlasCard {
                        Column {
                            InfoRow(Icons.Outlined.Landscape, "范围", period.territory)
                            InfoRow(Icons.Outlined.LocationCity, "枢纽", period.capital)
                            InfoRow(Icons.Outlined.Groups, "规模", period.population)
                            InfoRow(Icons.Outlined.Science, "核心", period.culture)
                        }
                    }
                }
            }

            // ---- 概述 ----
            if (period.summary.isNotBlank()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Column {
                                SectionHeader("概述")
                                Spacer(Modifier.height(8.dp))
                                Text(
                                    text = period.summary,
                                    color = InkSecondary,
                                    fontSize = 14.sp,
                                    lineHeight = 24.sp,
                                )
                            }
                        }
                    }
                }
            }

            // ---- 标签 ----
            if (period.tags.isNotEmpty()) {
                item {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 14.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        period.tags.take(8).forEach { tag ->
                            com.scienceatlas.app.ui.components.TagChip(tag)
                        }
                    }
                }
            }

            // ---- 子分期 ----
            if (children.isNotEmpty()) {
                item {
                    Column {
                        Box(Modifier.padding(horizontal = 14.dp)) {
                            SectionHeader("子分期", trailing = "${children.size} 个")
                        }
                        Spacer(Modifier.height(8.dp))
                        LazyRow(
                            contentPadding = PaddingValues(horizontal = 14.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            items(children, key = { it.id }) { child ->
                                ChildPeriodCard(child, onClick = { onChildPeriodClick(child) })
                            }
                        }
                    }
                }
            }

            // ---- 关键人物 ----
            if (figures.isNotEmpty()) {
                item {
                    Column {
                        Box(Modifier.padding(horizontal = 14.dp)) {
                            SectionHeader("关键人物", trailing = "${figures.size} 位")
                        }
                        Spacer(Modifier.height(8.dp))
                        LazyRow(
                            contentPadding = PaddingValues(horizontal = 14.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            items(figures, key = { it.id }) { figure ->
                                FigureChip(
                                    figure = figure,
                                    onClick = { onFigureClick(figure) },
                                )
                            }
                        }
                    }
                }
            }

            // ---- 代表事件 ----
            item {
                Box(Modifier.padding(horizontal = 14.dp)) {
                    SectionHeader("代表事件", trailing = "${events.size} 条")
                }
            }

            if (events.isEmpty()) {
                item {
                    EmptyHint("本分期暂无详细事件条目")
                }
            } else {
                items(events.take(300), key = { it.id }) { event ->
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        EventRow(event, onClick = { onEventClick(event) })
                    }
                }
            }
        }
    }
}

/** 详情页通用顶栏。 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun DetailTopBar(title: String, onBack: () -> Unit) {
    TopAppBar(
        title = {
            Text(
                text = title,
                fontSize = 17.sp,
                fontWeight = FontWeight.SemiBold,
                color = InkPrimary,
                maxLines = 1,
            )
        },
        navigationIcon = {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "返回",
                    tint = InkSecondary,
                )
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = Paper),
    )
}

/** 子分期卡片。 */
@Composable
internal fun ChildPeriodCard(period: Period, onClick: () -> Unit) {
    val colors = colorFor(period.colorKey, period.id)
    Column(
        modifier = Modifier
            .width(140.dp)
            .background(colors.block, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
    ) {
        Text(
            text = period.name,
            color = colors.accent,
            fontWeight = FontWeight.Bold,
            fontSize = 15.sp,
        )
        Spacer(Modifier.height(4.dp))
        Text(
            text = period.yearRangeText,
            color = InkTertiary,
            fontSize = 10.sp,
            lineHeight = 14.sp,
        )
    }
}

/** 人物小卡片（横向滚动用）。 */
@Composable
internal fun FigureChip(figure: Figure, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .width(76.dp)
            .clickable(onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        FigureAvatar(
            name = figure.name,
            role = figure.role,
            size = 48,
        )
        Spacer(Modifier.height(5.dp))
        Text(
            text = figure.name,
            color = InkPrimary,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            maxLines = 1,
        )
        Text(
            text = figure.lifeText.ifBlank { figure.role },
            color = InkTertiary,
            fontSize = 9.sp,
            maxLines = 1,
        )
    }
}

/** 事件列表行。 */
@Composable
internal fun EventRow(event: Event, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        // 日期列
        Column(
            modifier = Modifier.width(74.dp),
        ) {
            Text(
                text = event.dateText.ifBlank { "—" },
                color = MaterialTheme.colorScheme.primary,
                fontSize = 11.sp,
                fontWeight = FontWeight.Medium,
                lineHeight = 15.sp,
            )
        }
        Spacer(Modifier.width(6.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = event.name,
                color = InkPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                lineHeight = 20.sp,
            )
            Spacer(Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                CategoryBadge(EventCategory.from(event.category))
                if (event.location.isNotBlank()) {
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = event.location,
                        color = InkTertiary,
                        fontSize = 10.sp,
                        maxLines = 1,
                    )
                }
            }
        }
        Spacer(Modifier.width(8.dp))
        ImportanceStars(event.importance, compact = true)
    }
}
