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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Event
import com.scienceatlas.app.data.Figure
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.components.AtlasCard
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.FigureAvatar
import com.scienceatlas.app.ui.components.QuoteCard
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft
import com.scienceatlas.app.ui.theme.Paper

/**
 * 人物详情页。
 *
 * 结构：头像区 → 简介 → 生平 → 主要成就 → 名言 → 相关事件 → 相关人物。
 */
@Composable
fun FigureDetailScreen(
    repository: ScienceRepository,
    figureId: String,
    scope: String,
    onBack: () -> Unit,
    onEventClick: (Event) -> Unit,
    onFigureClick: (Figure) -> Unit,
    onPeriodClick: (Period) -> Unit,
) {
    val figure = remember(figureId, scope) { repository.figure(figureId, scope) }

    if (figure == null) {
        Scaffold(containerColor = Paper, topBar = { DetailTopBar("人物不存在", onBack) }) { padding ->
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                EmptyHint("未找到该人物")
            }
        }
        return
    }

    val events = remember(figureId, scope) { repository.resolveEventIds(figure.relatedEvents, scope) }
    val relatives = remember(figureId, scope) {
        repository.resolveFigureIds(figure.relatedFigures, scope)
    }
    val period = remember(figureId, scope) { repository.period(figure.periodId, scope) }

    Scaffold(
        containerColor = Paper,
        topBar = { DetailTopBar(figure.name, onBack) },
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // ---- 头部 ----
            item {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp, vertical = 8.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    FigureAvatar(
                        name = figure.name,
                        role = figure.role,
                        size = 92,
                    )
                    Spacer(Modifier.height(10.dp))
                    Text(
                        text = figure.name,
                        color = InkPrimary,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                    )
                    if (figure.alias.isNotBlank()) {
                        Spacer(Modifier.height(4.dp))
                        Text(
                            text = figure.alias,
                            color = InkTertiary,
                            fontSize = 12.sp,
                        )
                    }
                    Spacer(Modifier.height(10.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        MetaPill(figure.lifeText.ifBlank { "生卒不详" })
                        MetaPill(figure.role.ifBlank { "人物" })
                    }
                    if (period != null) {
                        Spacer(Modifier.height(8.dp))
                        Text(
                            text = "${period.name} · ${period.yearRangeText}",
                            color = MaterialTheme.colorScheme.primary,
                            fontSize = 12.sp,
                            modifier = Modifier.clickable { onPeriodClick(period) },
                        )
                    }
                }
            }

            // ---- 简介 ----
            if (figure.summary.isNotBlank()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Text(
                                text = figure.summary,
                                color = InkSecondary,
                                fontSize = 14.sp,
                                lineHeight = 24.sp,
                            )
                        }
                    }
                }
            }

            // ---- 生平 ----
            if (figure.biography.isNotBlank()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Column {
                                SectionHeader("生平")
                                Spacer(Modifier.height(8.dp))
                                Text(
                                    text = figure.biography,
                                    color = InkSecondary,
                                    fontSize = 14.sp,
                                    lineHeight = 25.sp,
                                )
                            }
                        }
                    }
                }
            }

            // ---- 主要成就 ----
            if (figure.achievements.isNotEmpty()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        AtlasCard {
                            Column {
                                SectionHeader("主要成就")
                                Spacer(Modifier.height(8.dp))
                                figure.achievements.forEach { item ->
                                    Row(
                                        modifier = Modifier.padding(vertical = 4.dp),
                                        verticalAlignment = Alignment.Top,
                                    ) {
                                        Box(
                                            Modifier
                                                .padding(top = 7.dp)
                                                .size(5.dp)
                                                .background(
                                                    MaterialTheme.colorScheme.primary.copy(alpha = 0.6f),
                                                    CircleShape,
                                                ),
                                        )
                                        Spacer(Modifier.width(10.dp))
                                        Text(
                                            text = item,
                                            color = InkSecondary,
                                            fontSize = 13.sp,
                                            lineHeight = 21.sp,
                                            modifier = Modifier.weight(1f),
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // ---- 名言 ----
            if (figure.quotes.isNotEmpty()) {
                item {
                    Column(
                        modifier = Modifier.padding(horizontal = 14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        SectionHeader("名言")
                        figure.quotes.forEach { q ->
                            QuoteCard(quote = q, attribution = figure.name)
                        }
                    }
                }
            }

            // ---- 相关事件 ----
            if (events.isNotEmpty()) {
                item {
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        SectionHeader("相关事件", trailing = "${events.size} 条")
                    }
                }
                items(events, key = { it.id }) { event ->
                    Box(Modifier.padding(horizontal = 14.dp)) {
                        EventRow(event, onClick = { onEventClick(event) })
                    }
                }
            }

            // ---- 相关人物 ----
            if (relatives.isNotEmpty()) {
                item {
                    Column {
                        Box(Modifier.padding(horizontal = 14.dp)) {
                            SectionHeader("相关人物", trailing = "${relatives.size} 位")
                        }
                        Spacer(Modifier.height(8.dp))
                        LazyRow(
                            contentPadding = PaddingValues(horizontal = 14.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            items(relatives, key = { it.id }) { rel ->
                                FigureChip(rel, onClick = { onFigureClick(rel) })
                            }
                        }
                    }
                }
            }
        }
    }
}

/** 人物头部下的小标签。 */
@Composable
private fun MetaPill(text: String) {
    Box(
        modifier = Modifier
            .background(Color(0xFFE9EEF5), RoundedCornerShape(12.dp))
            .padding(horizontal = 10.dp, vertical = 4.dp),
    ) {
        Text(
            text = text,
            color = InkSecondary,
            fontSize = 11.sp,
        )
    }
}
