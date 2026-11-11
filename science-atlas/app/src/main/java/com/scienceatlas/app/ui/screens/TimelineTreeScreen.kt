package com.scienceatlas.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
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
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.data.splitByChronology
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.PeriodGroup
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft
import com.scienceatlas.app.ui.theme.Paper

/**
 * 分期总览页 —— 复刻参考图的「分块年表树」。
 *
 * 布局：
 * ```
 * [阶段脊柱] │ [子分期色块] │ [三级色块]
 * ```
 * 每个阶段是一个 [PeriodGroup]，内部按时间顺序纵向排列色块。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimelineTreeScreen(
    repository: ScienceRepository,
    scope: String,
    onPeriodClick: (Period) -> Unit,
    onSearch: () -> Unit,
    onBack: () -> Unit,
) {
    val allTop = remember(scope) { repository.topLevelPeriods(scope) }
    // 编年主干与专题补充分组。专题分组（跨尺度、理论视角等）无法排进主线，
    // 单独成组展示，避免它们互相重叠把主线挤没。
    val (mainEras, extraEras) = remember(allTop) { splitByChronology(allTop) }
    val childrenMap = remember(scope) {
        (mainEras + extraEras).associate { era ->
            era.id to repository.childrenOf(era.id, scope)
        }
    }
    val grandChildrenMap = remember(scope) {
        childrenMap.values.flatten().associate { child ->
            child.id to repository.childrenOf(child.id, scope)
        }
    }
    val maxSpan = remember(scope) {
        repository.periods(scope).maxOfOrNull { (it.endYear - it.startYear).coerceAtLeast(0L) } ?: 1L
    }

    var query by remember { mutableStateOf("") }
    val highlightIds = remember(query, scope) {
        if (query.isBlank()) {
            emptySet()
        } else {
            repository.search(query, scope).periods.map { it.id }.toSet()
        }
    }

    val discipline = DISCIPLINES.firstOrNull { it.scope == scope } ?: DISCIPLINES.first()

    Scaffold(
        containerColor = Paper,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "${discipline.label}分期年表",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = InkPrimary,
                        )
                        Text(
                            text = "${mainEras.size} 个主干阶段 · ${repository.periods(scope).size} 个分期",
                            fontSize = 11.sp,
                            color = InkTertiary,
                        )
                    }
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
                actions = {
                    IconButton(onClick = onSearch) {
                        Icon(
                            imageVector = Icons.Outlined.Search,
                            contentDescription = "搜索",
                            tint = InkSecondary,
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Paper),
            )
        },
    ) { padding ->
        if (allTop.isEmpty()) {
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                EmptyHint("内容数据未就绪，请稍后重试")
            }
            return@Scaffold
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(
                start = 14.dp, end = 14.dp, top = 8.dp, bottom = 28.dp,
            ),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // ---- 编年主干 ----
            items(mainEras, key = { it.id }) { era ->
                PeriodGroup(
                    era = era,
                    children = childrenMap[era.id].orEmpty(),
                    grandChildren = grandChildrenMap,
                    maxSpan = maxSpan,
                    onPeriodClick = onPeriodClick,
                    highlightIds = highlightIds,
                )
            }

            // ---- 专题补充分组 ----
            if (extraEras.isNotEmpty()) {
                item {
                    Column {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(top = 6.dp),
                        ) {
                            Box(
                                Modifier
                                    .width(3.dp)
                                    .height(15.dp)
                                    .background(
                                        MaterialTheme.colorScheme.primary.copy(alpha = 0.75f),
                                        RoundedCornerShape(2.dp),
                                    ),
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                text = "专题补充",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = InkPrimary,
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                text = "${extraEras.size} 个 · 跨尺度视角",
                                style = MaterialTheme.typography.labelSmall,
                                color = InkTertiary,
                            )
                        }
                        Spacer(Modifier.height(8.dp))
                        Box(
                            Modifier
                                .fillMaxWidth()
                                .background(Color(0xFFF2F5F9), RoundedCornerShape(10.dp))
                                .padding(horizontal = 10.dp, vertical = 8.dp),
                        ) {
                            Text(
                                text = "这些分期采用不同的时间尺度或观察视角，" +
                                    "无法与主干并排，故单独列出。",
                                color = InkTertiary,
                                fontSize = 11.sp,
                                lineHeight = 17.sp,
                            )
                        }
                    }
                }
                items(extraEras, key = { it.id }) { era ->
                    PeriodGroup(
                        era = era,
                        children = childrenMap[era.id].orEmpty(),
                        grandChildren = grandChildrenMap,
                        maxSpan = maxSpan,
                        onPeriodClick = onPeriodClick,
                        highlightIds = highlightIds,
                    )
                }
            }
        }
    }
}
