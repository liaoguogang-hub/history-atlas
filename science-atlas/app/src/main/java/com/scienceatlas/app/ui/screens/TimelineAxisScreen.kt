package com.scienceatlas.app.ui.screens
import androidx.compose.material3.IconButton
import androidx.compose.material3.Icon
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Search

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Event
import com.scienceatlas.app.data.EventCategory
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.MainViewModel
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.EventAxisChip
import com.scienceatlas.app.ui.components.FilterChip
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.components.TimelineAxis
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.Paper

/**
 * 时间轴页：横向缩放时间轴 + 分类筛选 + 选中事件预览。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimelineAxisScreen(
    repository: ScienceRepository,
    scope: String,
    onEventClick: (Event) -> Unit,
    onBack: () -> Unit,
    viewModel: MainViewModel,
) {
    val allEvents = remember(scope) { repository.eventsOfScope(scope) }
    val allPeriods = remember(scope) { repository.periods(scope) }
    val categories = remember(scope) {
        allEvents.map { EventCategory.from(it.category) }.distinct().sortedBy { it.ordinal }
    }

    var selectedCategories by remember(scope) { mutableStateOf(categories.toSet()) }
    var selectedEventId by remember(scope) { mutableStateOf<String?>(null) }
    var query by remember(scope) { mutableStateOf("") }
    // 搜索框默认收起，点右上角放大镜才展开——避免长期占用首屏高度
    var showSearch by remember(scope) { mutableStateOf(false) }

    val filtered = remember(allEvents, selectedCategories, query) {
        allEvents
            .filter { EventCategory.from(it.category) in selectedCategories }
            .filter { e ->
                query.isBlank() ||
                    e.name.contains(query, ignoreCase = true) ||
                    e.summary.contains(query, ignoreCase = true) ||
                    e.detail.contains(query, ignoreCase = true)
            }
    }
    val selectedEvent = remember(selectedEventId, filtered) {
        filtered.firstOrNull { it.id == selectedEventId }
    }

    // 视窗状态保存在 ViewModel 中，从事件详情返回时仍是离开前的位置与缩放
    val viewport = remember(scope) { viewModel.axisViewportOf(scope) }
    val discipline = DISCIPLINES.firstOrNull { it.scope == scope } ?: DISCIPLINES.first()

    Scaffold(
        containerColor = Paper,
        topBar = {
            TopAppBar(
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回",
                            tint = InkSecondary,
                        )
                    }
                },
                title = {
                    Column {
                        Text(
                            text = "${discipline.label}时间轴",
                            fontSize = 17.sp,
                            color = InkPrimary,
                        )
                        Text(
                            text = "${filtered.size} 个事件 · ${categories.size} 个分类",
                            fontSize = 11.sp,
                            color = InkTertiary,
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { showSearch = !showSearch }) {
                        Icon(
                            imageVector = if (showSearch) Icons.Filled.Close else Icons.Outlined.Search,
                            contentDescription = if (showSearch) "收起搜索" else "搜索",
                            tint = InkSecondary,
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Paper),
            )
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            // ---- 搜索（点右上角按钮展开）----
            if (showSearch) {
                com.scienceatlas.app.ui.components.AtlasSearchField(
                    value = query,
                    onValueChange = { query = it },
                    placeholder = "搜索事件名称或内容…",
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                )
            }

            // ---- 分类筛选 ----
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 14.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                categories.forEach { cat ->
                    FilterChip(
                        text = cat.label,
                        selected = cat in selectedCategories,
                        onClick = {
                            selectedCategories = if (cat in selectedCategories) {
                                selectedCategories - cat
                            } else {
                                selectedCategories + cat
                            }
                        },
                    )
                }
            }

            // ---- 时间轴画布（含分期带与年代刻度）----
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 14.dp, vertical = 2.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = "上方色带为分期 · 下方刻度每 100 年一格",
                    color = InkTertiary,
                    fontSize = 9.sp,
                )
                Text(
                    text = "捏合缩放 · 拖动平移",
                    color = InkTertiary,
                    fontSize = 9.sp,
                )
            }
            TimelineAxis(
                events = filtered,
                periods = allPeriods,
                viewport = viewport,
                onViewportChange = { viewModel.saveAxisViewport(scope, it) },
                onEventClick = { selectedEventId = it.id },
                selectedEventId = selectedEventId,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(320.dp),
            )

            // ---- 选中事件预览 ----
            if (selectedEvent != null) {
                Box(Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                    Row(
                        modifier = Modifier.clickable { onEventClick(selectedEvent) },
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        EventAxisChip(event = selectedEvent, modifier = Modifier.weight(1f))
                    }
                }
            } else {
                EmptyHint("点击时间轴上的标记查看事件详情")
            }

            // ---- 事件列表（按时间） ----
            SectionHeader(
                title = "事件流",
                trailing = "${filtered.size} 条",
                modifier = Modifier.padding(horizontal = 14.dp),
            )
            Spacer(Modifier.height(6.dp))

            LazyColumn(
                contentPadding = PaddingValues(14.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(filtered.take(400), key = { it.id }) { event ->
                    EventRow(event, onClick = { onEventClick(event) })
                }
            }
        }
    }
}
