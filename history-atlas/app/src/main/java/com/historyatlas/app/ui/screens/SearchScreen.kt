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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
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
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.historyatlas.app.data.Event
import com.historyatlas.app.data.Figure
import com.historyatlas.app.data.HistoryRepository
import com.historyatlas.app.data.Period
import com.historyatlas.app.ui.components.EmptyHint
import com.historyatlas.app.ui.components.HighlightedText
import com.historyatlas.app.ui.components.SectionHeader
import com.historyatlas.app.ui.theme.CardSurface
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.OutlineSoft
import com.historyatlas.app.ui.theme.Paper

/**
 * 搜索页：跨时期 / 事件 / 人物三类实时过滤。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    repository: HistoryRepository,
    scope: String,
    onPeriodClick: (Period) -> Unit,
    onEventClick: (Event) -> Unit,
    onFigureClick: (Figure) -> Unit,
    onBack: () -> Unit,
) {
    var query by remember { mutableStateOf("") }
    val keyboard = LocalSoftwareKeyboardController.current
    val result = remember(query, scope) { repository.search(query, scope) }

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
                    OutlinedTextField(
                        value = query,
                        onValueChange = { query = it },
                        placeholder = {
                            Text(
                                text = "搜索朝代、事件、人物…",
                                color = InkTertiary,
                                fontSize = 14.sp,
                            )
                        },
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Outlined.Search,
                                contentDescription = null,
                                tint = InkTertiary,
                                modifier = Modifier.size(18.dp),
                            )
                        },
                        trailingIcon = {
                            if (query.isNotEmpty()) {
                                IconButton(onClick = { query = "" }) {
                                    Icon(
                                        imageVector = Icons.Outlined.Close,
                                        contentDescription = "清空",
                                        tint = InkTertiary,
                                        modifier = Modifier.size(17.dp),
                                    )
                                }
                            }
                        },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                        keyboardActions = KeyboardActions(onSearch = { keyboard?.hide() }),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = OutlineSoft,
                            focusedContainerColor = CardSurface,
                            unfocusedContainerColor = CardSurface,
                        ),
                        modifier = Modifier.fillMaxWidth(),
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Paper),
            )
        },
    ) { padding ->
        if (query.isBlank()) {
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "试试搜索",
                        color = InkTertiary,
                        fontSize = 13.sp,
                    )
                    Spacer(Modifier.height(10.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        listOf("秦", "三国", "丝绸之路", "李白", "工业革命").forEach { hint ->
                            Box(
                                modifier = Modifier
                                    .background(Color(0xFFF0EBE1), RoundedCornerShape(12.dp))
                                    .clickable { query = hint }
                                    .padding(horizontal = 12.dp, vertical = 6.dp),
                            ) {
                                Text(hint, color = InkSecondary, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
            return@Scaffold
        }

        if (result.isEmpty) {
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                EmptyHint("没有找到「$query」相关内容")
            }
            return@Scaffold
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (result.periods.isNotEmpty()) {
                item {
                    SectionHeader("时期", trailing = "${result.periods.size} 个")
                }
                items(result.periods.take(30), key = { "p-${it.id}" }) { p ->
                    SearchPeriodRow(p, query) { onPeriodClick(p) }
                }
            }
            if (result.events.isNotEmpty()) {
                item {
                    Spacer(Modifier.height(6.dp))
                    SectionHeader("事件", trailing = "${result.events.size} 条")
                }
                items(result.events.take(60), key = { "e-${it.id}" }) { e ->
                    SearchEventRow(e, query) { onEventClick(e) }
                }
            }
            if (result.figures.isNotEmpty()) {
                item {
                    Spacer(Modifier.height(6.dp))
                    SectionHeader("人物", trailing = "${result.figures.size} 位")
                }
                items(result.figures.take(60), key = { "f-${it.id}" }) { f ->
                    SearchFigureRow(f, query) { onFigureClick(f) }
                }
            }
        }
    }
}

/** 搜索结果：时期行。 */
@Composable
private fun SearchPeriodRow(period: Period, query: String, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            HighlightedText(
                text = period.name,
                query = query,
                style = MaterialTheme.typography.titleSmall,
                color = InkPrimary,
            )
            Spacer(Modifier.height(2.dp))
            HighlightedText(
                text = period.yearRangeText,
                query = query,
                style = MaterialTheme.typography.labelSmall,
                color = InkTertiary,
            )
        }
    }
}

/** 搜索结果：事件行。 */
@Composable
private fun SearchEventRow(event: Event, query: String, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            HighlightedText(
                text = event.name,
                query = query,
                style = MaterialTheme.typography.bodyMedium,
                color = InkPrimary,
            )
            Spacer(Modifier.height(3.dp))
            HighlightedText(
                text = "${event.dateText} · ${event.summary}",
                query = query,
                style = MaterialTheme.typography.labelSmall,
                color = InkTertiary,
                maxLines = 2,
            )
        }
    }
}

/** 搜索结果：人物行。 */
@Composable
private fun SearchFigureRow(figure: Figure, query: String, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        com.historyatlas.app.ui.components.FigureAvatar(
            name = figure.name,
            role = figure.role,
            size = 38,
        )
        Spacer(Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            HighlightedText(
                text = figure.name,
                query = query,
                style = MaterialTheme.typography.bodyMedium,
                color = InkPrimary,
            )
            Spacer(Modifier.height(3.dp))
            HighlightedText(
                text = "${figure.role} · ${figure.lifeText}",
                query = query,
                style = MaterialTheme.typography.labelSmall,
                color = InkTertiary,
                maxLines = 1,
            )
        }
    }
}
