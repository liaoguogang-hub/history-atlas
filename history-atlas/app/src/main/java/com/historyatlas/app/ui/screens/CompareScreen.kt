package com.historyatlas.app.ui.screens
import androidx.compose.material.icons.Icons
import androidx.compose.material3.IconButton
import androidx.compose.material3.Icon
import androidx.compose.material.icons.automirrored.filled.ArrowBack

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
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
import com.historyatlas.app.data.splitByChronology
import com.historyatlas.app.ui.components.EmptyHint
import com.historyatlas.app.ui.components.FilterChip
import com.historyatlas.app.ui.components.SectionHeader
import com.historyatlas.app.ui.theme.CardSurface
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.OutlineSoft
import com.historyatlas.app.ui.theme.Paper
import com.historyatlas.app.ui.theme.colorFor

/**
 * 中外对照页：把中国史与世界史的时期并排放，按时间轴同步。
 *
 * 交互：左右两个列表，共享一个「聚焦年代」滑块。
 * 移动滑块时，两侧各自高亮与该年代有交集的时期。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompareScreen(
    repository: HistoryRepository,
    chinaScope: String,
    worldScope: String,
    onPeriodClick: (String, String) -> Unit,
    onBack: () -> Unit,
) {
    val chinaPeriods = remember(chinaScope) { repository.topLevelPeriods(chinaScope) }
    val worldPeriods = remember(worldScope) { repository.topLevelPeriods(worldScope) }

    // 编年主干优先展示，区域专题作为补充分组
    val (chinaMain, chinaExtra) = remember(chinaPeriods) { splitByChronology(chinaPeriods) }
    val (worldMain, worldExtra) = remember(worldPeriods) { splitByChronology(worldPeriods) }

    // 聚焦年代（公元年）
    var focusYear by remember { mutableStateOf(1400) }
    // 每次显式选年代时自增，触发两侧列表滚动到对应朝代。
    // 与 focusYear 分开是为了区分「用户点了年代」（要滚动）
    // 和「用户自己滚列表」（不要被拉回去）。
    var scrollSignal by remember { mutableStateOf(0) }
    val minYear = remember(chinaPeriods, worldPeriods) {
        minOf(
            chinaPeriods.minOfOrNull { it.startYear } ?: -3000,
            worldPeriods.minOfOrNull { it.startYear } ?: -3000,
        )
    }
    val maxYear = remember(chinaPeriods, worldPeriods) {
        maxOf(
            chinaPeriods.maxOfOrNull { it.endYear } ?: 2026,
            worldPeriods.maxOfOrNull { it.endYear } ?: 2026,
        )
    }

    fun matches(p: Period) = focusYear in p.startYear..p.endYear

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
                        Text(text = "中外对照", fontSize = 17.sp, color = InkPrimary)
                        Text(
                            text = "拖动年代，看两个世界同时发生了什么",
                            fontSize = 11.sp,
                            color = InkTertiary,
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
            // ---- 年代焦点 ----
            FocusYearBar(
                focusYear = focusYear,
                minYear = minYear,
                maxYear = maxYear,
                onChange = {
                    focusYear = it
                    scrollSignal++
                },
            )

            Spacer(Modifier.height(10.dp))

            // ---- 双列对照 ----
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(horizontal = 14.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                CompareColumn(
                    title = "中国史",
                    periods = chinaMain,
                    scope = chinaScope,
                    focusYear = focusYear,
                    scrollSignal = scrollSignal,
                    onPeriodClick = { onPeriodClick(it.id, chinaScope) },
                    modifier = Modifier.weight(1f),
                )
                CompareColumn(
                    title = "世界史",
                    periods = worldMain,
                    scope = worldScope,
                    focusYear = focusYear,
                    scrollSignal = scrollSignal,
                    onPeriodClick = { onPeriodClick(it.id, worldScope) },
                    modifier = Modifier.weight(1f),
                )
            }

            // ---- 专题补充 ----
            // 中国史与世界史的补充组都要渲染。早先只渲染了世界史的补充组，
            // 一旦中国史里有时期被划进补充组就会整体消失（表现为「查某年时中国史空白」）。
            val extras = buildList {
                chinaExtra.forEach { add(it to chinaScope) }
                worldExtra.forEach { add(it to worldScope) }
            }
            if (extras.isNotEmpty()) {
                Spacer(Modifier.height(10.dp))
                Box(Modifier.padding(horizontal = 14.dp)) {
                    SectionHeader("专题补充", trailing = "跨朝代视角")
                }
                Spacer(Modifier.height(6.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 14.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    extras.forEach { (p, sc) ->
                        val active = focusYear in p.startYear..p.endYear
                        ComparePeriodCard(
                            period = p,
                            active = active,
                            onClick = { onPeriodClick(p.id, sc) },
                            modifier = Modifier.width(170.dp),
                        )
                    }
                }
            }
        }
    }
}

/**
 * 把顶层时期按「编年主干 / 区域专题」拆分。
 *
 * 委托给 `com.historyatlas.app.data.splitByChronology`：
 * 以区间重叠检测为主干判定（正统朝代优先），并识别数据中显式标注的「区域专题」。
 */

/** 年代焦点滑块。 */
@Composable
private fun FocusYearBar(
    focusYear: Int,
    minYear: Int,
    maxYear: Int,
    onChange: (Int) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "聚焦年代",
                color = InkTertiary,
                fontSize = 12.sp,
            )
            Box(
                modifier = Modifier
                    .background(Color(0xFFE8F0EE), RoundedCornerShape(10.dp))
                    .padding(horizontal = 12.dp, vertical = 4.dp),
            ) {
                Text(
                    text = if (focusYear < 0) "公元前${-focusYear}年" else "公元${focusYear}年",
                    color = MaterialTheme.colorScheme.primary,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
        Spacer(Modifier.height(6.dp))
        // 年代按钮改为 100 年一档，可横向滚动。
        // 早先用 500 年一档（前2000/前500/0/500/1000…），跨度太大，
        // 想定位到具体朝代时几乎对不上。
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            val presets = buildList {
                var y = -2000
                while (y <= 2000) {
                    add(y)
                    y += 100
                }
            }
            presets.forEach { y ->
                val selected = focusYear == y
                Box(
                    modifier = Modifier
                        .background(
                            if (selected) MaterialTheme.colorScheme.primary else Color(0xFFF0EBE1),
                            RoundedCornerShape(6.dp),
                        )
                        .clickable { onChange(y) }
                        .padding(horizontal = 11.dp, vertical = 6.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = if (y < 0) "前${-y}" else "${y}",
                        color = if (selected) Color.White else InkSecondary,
                        fontSize = 9.sp,
                        maxLines = 1,
                    )
                }
            }
        }
    }
}

/** 对照页单侧列表。 */
@Composable
private fun CompareColumn(
    title: String,
    periods: List<Period>,
    scope: String,
    focusYear: Int,
    scrollSignal: Int,
    onPeriodClick: (Period) -> Unit,
    modifier: Modifier = Modifier,
) {
    val listState = rememberLazyListState()

    // 用户点了年代（scrollSignal 变化）后，自动滚到该年代对应的朝代，
    // 两侧各自定位到自己的时期，实现「点一个年代，两个世界同时跳转」。
    LaunchedEffect(scrollSignal, periods, focusYear) {
        if (scrollSignal == 0 || periods.isEmpty()) return@LaunchedEffect
        val idx = periods.indexOfFirst { focusYear in it.startYear..it.endYear }
        if (idx >= 0) {
            listState.animateScrollToItem(idx)
        } else {
            // 该年代落在两个时期之间的空档：滚到最近的那个时期
            val nearest = periods.indices.minByOrNull { i ->
                val p = periods[i]
                when {
                    focusYear < p.startYear -> p.startYear - focusYear
                    focusYear > p.endYear -> focusYear - p.endYear
                    else -> 0
                }
            }
            if (nearest != null) listState.animateScrollToItem(nearest)
        }
    }

    Column(modifier = modifier) {
        SectionHeader(title)
        Spacer(Modifier.height(8.dp))
        LazyColumn(
            state = listState,
            contentPadding = PaddingValues(bottom = 20.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            items(periods, key = { it.id }) { period ->
                val active = focusYear in period.startYear..period.endYear
                ComparePeriodCard(
                    period = period,
                    active = active,
                    onClick = { onPeriodClick(period) },
                )
            }
            if (periods.isEmpty()) {
                item { EmptyHint("暂无数据") }
            }
        }
    }
}

/** 对照页时期卡片：命中年代的高亮。 */
@Composable
private fun ComparePeriodCard(
    period: Period,
    active: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = colorFor(period.colorKey, period.id)
    Box(
        modifier = modifier
            .fillMaxWidth()
            .background(
                if (active) colors.block else CardSurface,
                RoundedCornerShape(9.dp),
            )
            .clickable(onClick = onClick)
            .then(
                if (active) {
                    Modifier.border(
                        width = 1.5.dp,
                        color = colors.accent.copy(alpha = 0.5f),
                        shape = RoundedCornerShape(9.dp),
                    )
                } else {
                    Modifier.border(1.dp, OutlineSoft, RoundedCornerShape(9.dp))
                },
            )
            .padding(10.dp),
    ) {
        Column {
            Text(
                text = period.name,
                color = if (active) colors.accent else InkPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
            )
            Spacer(Modifier.height(3.dp))
            Text(
                text = period.yearRangeText,
                color = if (active) InkSecondary else InkTertiary,
                fontSize = 10.sp,
                maxLines = 1,
            )
            if (active && period.summary.isNotBlank()) {
                Spacer(Modifier.height(5.dp))
                Text(
                    text = period.summary,
                    color = InkSecondary,
                    fontSize = 11.sp,
                    lineHeight = 16.sp,
                    maxLines = 4,
                )
            }
        }
    }
}
