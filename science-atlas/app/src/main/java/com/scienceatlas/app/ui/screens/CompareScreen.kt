package com.scienceatlas.app.ui.screens
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.data.splitByChronology
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.FilterChip
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft
import com.scienceatlas.app.ui.theme.Paper
import com.scienceatlas.app.ui.theme.colorFor

/**
 * 四科对照页：任选两门学科，把分期并排放，按同一「聚焦年代」同步高亮。
 *
 * 交互：左右两个列表，共享一个「聚焦年代」滑块。
 * 移动滑块时，两侧各自高亮与该年代有交集的分期；
 * 显式选择年代时，两侧自动滚动到各自对应的那一条。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompareScreen(
    repository: ScienceRepository,
    scope: String,
    onScopeChange: (String) -> Unit,
    onBack: () -> Unit,
) {
    // 左列默认为当前学科，右列默认为它的下一门学科。
    val leftIndex = remember(scope) { DISCIPLINES.indexOfFirst { it.scope == scope }.coerceAtLeast(0) }
    var leftScope by remember(scope) { mutableStateOf(DISCIPLINES[leftIndex].scope) }
    var rightScope by remember(scope) {
        mutableStateOf(DISCIPLINES[(leftIndex + 1) % DISCIPLINES.size].scope)
    }

    val leftPeriods = remember(leftScope) { repository.topLevelPeriods(leftScope) }
    val rightPeriods = remember(rightScope) { repository.topLevelPeriods(rightScope) }

    // 编年主干优先展示，专题作为补充分组
    val (leftMain, leftExtra) = remember(leftPeriods) { splitByChronology(leftPeriods) }
    val (rightMain, rightExtra) = remember(rightPeriods) { splitByChronology(rightPeriods) }

    // 聚焦年代（公元年）
    var focusYear by remember { mutableStateOf(1900L) }
    // 每次显式选年代时自增，触发两侧列表滚动到对应分期。
    // 与 focusYear 分开是为了区分「用户点了年代」（要滚动）
    // 和「用户自己滚列表」（不要被拉回去）。
    var scrollSignal by remember { mutableStateOf(0) }
    val minYear = remember(leftPeriods, rightPeriods) {
        minOf(
            leftPeriods.minOfOrNull { it.startYear } ?: -3000L,
            rightPeriods.minOfOrNull { it.startYear } ?: -3000L,
        )
    }
    val maxYear = remember(leftPeriods, rightPeriods) {
        maxOf(
            leftPeriods.maxOfOrNull { it.endYear } ?: 2026L,
            rightPeriods.maxOfOrNull { it.endYear } ?: 2026L,
        )
    }

    val leftLabel = DISCIPLINES.firstOrNull { it.scope == leftScope }?.label ?: leftScope
    val rightLabel = DISCIPLINES.firstOrNull { it.scope == rightScope }?.label ?: rightScope

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
                        Text(text = "四科对照", fontSize = 17.sp, color = InkPrimary)
                        Text(
                            text = "选一个年代，看两门科学同时发生了什么",
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
            // ---- 学科选择 ----
            Column(
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("左列", color = InkTertiary, fontSize = 11.sp)
                    DISCIPLINES.forEach { d ->
                        FilterChip(
                            text = d.label,
                            selected = leftScope == d.scope,
                            onClick = { leftScope = d.scope },
                        )
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("右列", color = InkTertiary, fontSize = 11.sp)
                    DISCIPLINES.forEach { d ->
                        FilterChip(
                            text = d.label,
                            selected = rightScope == d.scope,
                            onClick = { rightScope = d.scope },
                        )
                    }
                }
            }

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
                    title = leftLabel,
                    periods = leftMain,
                    scope = leftScope,
                    focusYear = focusYear,
                    scrollSignal = scrollSignal,
                    onPeriodClick = { onScopeChange(leftScope) },
                    modifier = Modifier.weight(1f),
                )
                CompareColumn(
                    title = rightLabel,
                    periods = rightMain,
                    scope = rightScope,
                    focusYear = focusYear,
                    scrollSignal = scrollSignal,
                    onPeriodClick = { onScopeChange(rightScope) },
                    modifier = Modifier.weight(1f),
                )
            }

            // ---- 专题补充 ----
            // 两侧的补充组都要渲染。早先只渲染了一侧的补充组，
            // 一旦另一侧有分期被划进补充组就会整体消失（表现为「查某年时某学科空白」）。
            val extras = buildList {
                leftExtra.forEach { add(it to leftScope) }
                rightExtra.forEach { add(it to rightScope) }
            }
            if (extras.isNotEmpty()) {
                Spacer(Modifier.height(10.dp))
                Box(Modifier.padding(horizontal = 14.dp)) {
                    SectionHeader("专题补充", trailing = "跨尺度视角")
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
                            onClick = { onScopeChange(sc) },
                            modifier = Modifier.width(170.dp),
                        )
                    }
                }
            }
        }
    }
}

/** 年代焦点滑块。 */
@Composable
private fun FocusYearBar(
    focusYear: Long,
    minYear: Long,
    maxYear: Long,
    onChange: (Long) -> Unit,
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
                    .background(Color(0xFFE3EBF7), RoundedCornerShape(10.dp))
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
        // 早先用 500 年一档，跨度太大，想定位到具体分期时几乎对不上。
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            val presets = buildList {
                var y = -2000L
                while (y <= 2000L) {
                    add(y)
                    y += 100
                }
            }
            presets.forEach { y ->
                val selected = focusYear == y
                Box(
                    modifier = Modifier
                        .background(
                            if (selected) MaterialTheme.colorScheme.primary else Color(0xFFE9EEF5),
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
    focusYear: Long,
    scrollSignal: Int,
    onPeriodClick: (Period) -> Unit,
    modifier: Modifier = Modifier,
) {
    val listState = rememberLazyListState()

    // 用户点了年代（scrollSignal 变化）后，自动滚到该年代对应的分期，
    // 两侧各自定位到自己的分期，实现「点一个年代，两门科学同时跳转」。
    LaunchedEffect(scrollSignal, periods, focusYear) {
        if (scrollSignal == 0 || periods.isEmpty()) return@LaunchedEffect
        val idx = periods.indexOfFirst { focusYear in it.startYear..it.endYear }
        if (idx >= 0) {
            listState.animateScrollToItem(idx)
        } else {
            // 该年代落在两个分期之间的空档：滚到最近的那个分期
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

/** 对照页分期卡片：命中年代的高亮。 */
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
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}
