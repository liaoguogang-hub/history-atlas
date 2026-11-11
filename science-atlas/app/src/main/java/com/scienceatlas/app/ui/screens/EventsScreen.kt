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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Event
import com.scienceatlas.app.data.EventCategory
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.components.AtlasSearchField
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.FilterChip
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.Paper

/**
 * 发现流页：按时间倒序 + 分类筛选。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EventsScreen(
    repository: ScienceRepository,
    scope: String,
    onEventClick: (Event) -> Unit,
    onBack: () -> Unit,
) {
    val allEvents = remember(scope) { repository.eventsOfScope(scope) }
    val categories = remember(scope) {
        allEvents.map { EventCategory.from(it.category) }.distinct().sortedBy { it.ordinal }
    }

    var selected by remember(scope) { mutableStateOf(categories.toSet()) }
    var importantOnly by remember(scope) { mutableStateOf(false) }
    var query by remember(scope) { mutableStateOf("") }
    var showSearch by remember(scope) { mutableStateOf(false) }

    val filtered = remember(allEvents, selected, importantOnly, query) {
        allEvents
            .filter { EventCategory.from(it.category) in selected }
            .filter { !importantOnly || it.importance >= 4 }
            .filter { e ->
                query.isBlank() ||
                    e.name.contains(query, ignoreCase = true) ||
                    e.summary.contains(query, ignoreCase = true) ||
                    e.detail.contains(query, ignoreCase = true)
            }
            // 先按重要度降序，同重要度按年代升序（自古而今）：
            // 若只按年份排，近现代同年事件会成片堆在一起；
            // 而"重要事件"视图的语义本就应当把最重大的节点前置，
            // 并在同一层级内保持编年的阅读顺序。
            .sortedWith(
                compareByDescending<Event> { it.importance }
                    .thenBy { it.year }
            )
    }

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
                        Text(text = "${discipline.label}·发现流", fontSize = 17.sp, color = InkPrimary)
                        Text(
                            text = "共 ${allEvents.size} 条 · 当前 ${filtered.size} 条",
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
            if (showSearch) {
                AtlasSearchField(
                    value = query,
                    onValueChange = { query = it },
                    placeholder = "搜索事件名称或内容…",
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                )
            }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 14.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                FilterChip(
                    text = "重要事件",
                    selected = importantOnly,
                    onClick = { importantOnly = !importantOnly },
                )
                categories.forEach { cat ->
                    FilterChip(
                        text = cat.label,
                        selected = cat in selected,
                        onClick = {
                            selected = if (cat in selected) selected - cat else selected + cat
                        },
                    )
                }
            }

            if (filtered.isEmpty()) {
                EmptyHint("没有符合条件的事件")
                return@Column
            }

            LazyColumn(
                contentPadding = PaddingValues(14.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(filtered, key = { it.id }) { event ->
                    EventRow(event, onClick = { onEventClick(event) })
                }
            }
        }
    }
}
