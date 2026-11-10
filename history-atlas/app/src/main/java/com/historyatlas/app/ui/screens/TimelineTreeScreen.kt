package com.historyatlas.app.ui.screens

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
import com.historyatlas.app.data.HistoryRepository
import com.historyatlas.app.data.Period
import com.historyatlas.app.ui.components.EmptyHint
import com.historyatlas.app.ui.components.PeriodGroup
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.OutlineSoft
import com.historyatlas.app.ui.theme.Paper

/**
 * 年表总览页 —— 复刻参考图的「分块年表树」。
 *
 * 布局：
 * ```
 * [时代脊柱] │ [子时期色块] │ [三级色块]
 * ```
 * 每个时代是一个 [PeriodGroup]，内部按时间顺序纵向排列色块。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimelineTreeScreen(
    repository: HistoryRepository,
    scope: String,
    onPeriodClick: (Period) -> Unit,
    onSearch: () -> Unit,
    onBack: () -> Unit,
) {
    val eras = remember(scope) { repository.topLevelPeriods(scope) }
    val childrenMap = remember(scope) {
        eras.associate { era ->
            era.id to repository.childrenOf(era.id, scope)
        }
    }
    val grandChildrenMap = remember(scope) {
        childrenMap.values.flatten().associate { child ->
            child.id to repository.childrenOf(child.id, scope)
        }
    }
    val maxSpan = remember(scope) {
        repository.periods(scope).maxOfOrNull { (it.endYear - it.startYear).coerceAtLeast(0) } ?: 1
    }

    var query by remember { mutableStateOf("") }
    val highlightIds = remember(query, scope) {
        if (query.isBlank()) {
            emptySet()
        } else {
            repository.search(query, scope).periods.map { it.id }.toSet()
        }
    }

    Scaffold(
        containerColor = Paper,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = if (scope == HistoryRepository.SCOPE_WORLD) "世界史年表" else "中国史年表",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = InkPrimary,
                        )
                        Text(
                            text = "${eras.size} 个时代 · ${repository.periods(scope).size} 个时期",
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
        if (eras.isEmpty()) {
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
            items(eras, key = { it.id }) { era ->
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
