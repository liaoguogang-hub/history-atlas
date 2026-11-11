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
import androidx.compose.foundation.layout.size
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scienceatlas.app.data.Figure
import com.scienceatlas.app.data.Period
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.components.AtlasSearchField
import com.scienceatlas.app.ui.components.EmptyHint
import com.scienceatlas.app.ui.components.FigureAvatar
import com.scienceatlas.app.ui.components.FilterChip
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.Paper

/**
 * 科学家志页：按身份筛选 + 按分期分组浏览。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FiguresScreen(
    repository: ScienceRepository,
    scope: String,
    onFigureClick: (Figure) -> Unit,
    onBack: () -> Unit,
) {
    val allFigures = remember(scope) { repository.figuresOfScope(scope) }
    val periods = remember(scope) { repository.periods(scope) }

    var roleFilter by remember(scope) { mutableStateOf("") }
    var periodFilter by remember(scope) { mutableStateOf("") }
    var subPeriodFilter by remember(scope) { mutableStateOf("") }
    var query by remember(scope) { mutableStateOf("") }
    var showSearch by remember(scope) { mutableStateOf(false) }

    val roles = remember(allFigures) {
        allFigures.map { it.role }.filter { it.isNotBlank() }.distinct().sorted()
    }
    val topPeriods = remember(periods) { periods.filter { it.parentId == null } }

    // 每个人物挂的是叶子分期（如「地磁学革命」），而筛选栏列出的是顶层分期
    // （如「近代地球科学」）。这里预先把每个分期的整棵子树展开成集合，
    // 否则按顶层分期筛选会因为精确匹配不上而一个人物都筛不出来。
    val subtree = remember(periods) {
        val byParent = periods.groupBy { it.parentId }
        val cache = HashMap<String, Set<String>>()
        fun collect(id: String, visiting: MutableSet<String>): Set<String> {
            cache[id]?.let { return it }
            if (!visiting.add(id)) return setOf(id)   // 防御性：避免成环
            val acc = mutableSetOf(id)
            byParent[id].orEmpty().forEach { acc.addAll(collect(it.id, visiting)) }
            visiting.remove(id)
            val result = acc.toSet()
            cache[id] = result
            return result
        }
        periods.associate { it.id to collect(it.id, mutableSetOf()) }
    }

    val filtered = remember(allFigures, roleFilter, periodFilter, subPeriodFilter,
                            subtree, query) {
        allFigures.filter { f ->
            (roleFilter.isEmpty() || f.role == roleFilter) &&
                (periodFilter.isEmpty() ||
                    (subtree[periodFilter]?.contains(f.periodId) == true)) &&
                // 选了子分期时，只保留挂在该子分期或其子树上的人物
                (subPeriodFilter.isEmpty() ||
                    (subtree[subPeriodFilter]?.contains(f.periodId) == true)) &&
                (query.isBlank() ||
                    f.name.contains(query, ignoreCase = true) ||
                    f.alias.contains(query, ignoreCase = true) ||
                    f.role.contains(query, ignoreCase = true) ||
                    f.summary.contains(query, ignoreCase = true) ||
                    f.biography.contains(query, ignoreCase = true))
        }
    }

    // 按分期分组
    //
    // 组内排序不用纯拼音：一组动辄五十多人，纯拼音下核心人物会埋在中后段，
    // 翻找成本很高。改用「关联数量 + 传记长度」作为权重，
    // 让分量重的人物排在前面，同权重时再按姓名拼音兜底。
    val grouped = remember(filtered, periods) {
        fun weight(f: Figure): Int {
            val links = f.relatedFigures.size + f.relatedEvents.size
            val bio = f.biography.length
            val quote = f.quotes.size
            return links * 100 + bio / 10 + quote * 5
        }
        filtered.groupBy { it.periodId }
            .mapNotNull { (pid, list) ->
                periods.firstOrNull { it.id == pid }?.let { it to list }
            }
            .sortedBy { it.first.startYear }
            .map { (period, list) ->
                period to list.sortedWith(
                    compareByDescending<Figure> { weight(it) }.thenBy { it.name }
                )
            }
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
                        Text(text = "${discipline.label}·科学家志", fontSize = 17.sp, color = InkPrimary)
                        Text(
                            text = "${allFigures.size} 位科学家",
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
                AtlasSearchField(
                    value = query,
                    onValueChange = { query = it },
                    placeholder = "搜索科学家姓名、身份或生平…",
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                )
            }

            // ---- 分期筛选 ----
            // 两级：先选顶层分期，再选其下的子分期。
            // 只有一个顶层分期时，几十位科学家挤在一个分组里，
            // 想找某位关键人物要翻很久——加上子分期筛选才好定位。
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 14.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                FilterChip(
                    text = "全部分期",
                    selected = periodFilter.isEmpty(),
                    onClick = { periodFilter = ""; subPeriodFilter = "" },
                )
                topPeriods.take(14).forEach { p ->
                    FilterChip(
                        text = p.name,
                        selected = periodFilter == p.id,
                        onClick = {
                            // 再次点击已选中的顶层分期 → 取消筛选
                            periodFilter = if (periodFilter == p.id) "" else p.id
                            subPeriodFilter = ""
                        },
                    )
                }
            }

            // ---- 子分期筛选：仅在顶层分期已选中且它有子分期时出现 ----
            if (periodFilter.isNotEmpty()) {
                val children = remember(periods, periodFilter) {
                    periods.filter { it.parentId == periodFilter }
                        .sortedBy { it.startYear }
                }
                if (children.isNotEmpty()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState())
                            .padding(horizontal = 14.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        children.forEach { c ->
                            FilterChip(
                                text = c.name,
                                selected = subPeriodFilter == c.id,
                                onClick = {
                                    subPeriodFilter =
                                        if (subPeriodFilter == c.id) "" else c.id
                                },
                            )
                        }
                    }
                }
            }

            // ---- 身份筛选 ----
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 14.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                FilterChip(
                    text = "全部身份",
                    selected = roleFilter.isEmpty(),
                    onClick = { roleFilter = "" },
                )
                roles.take(30).forEach { r ->
                    FilterChip(
                        text = r,
                        selected = roleFilter == r,
                        onClick = { roleFilter = if (roleFilter == r) "" else r },
                    )
                }
            }

            Spacer(Modifier.height(8.dp))

            if (filtered.isEmpty()) {
                EmptyHint("没有符合条件的科学家")
                return@Column
            }

            LazyColumn(
                contentPadding = PaddingValues(14.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                grouped.forEach { (period, list) ->
                    item(key = "h-${period.id}") {
                        SectionHeader(
                            title = period.name,
                            trailing = "${list.size} 位 · ${period.yearRangeText}",
                        )
                    }
                    items(list, key = { it.id }) { figure ->
                        FigureRow(figure, onClick = { onFigureClick(figure) })
                    }
                }
            }
        }
    }
}

/** 科学家列表行。 */
@Composable
internal fun FigureRow(figure: Figure, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        FigureAvatar(name = figure.name, role = figure.role, size = 44)
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = figure.name,
                    color = InkPrimary,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                )
                if (figure.alias.isNotBlank()) {
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = figure.alias,
                        color = InkTertiary,
                        fontSize = 10.sp,
                        maxLines = 1,
                    )
                }
            }
            Spacer(Modifier.height(3.dp))
            Text(
                text = "${figure.role} · ${figure.lifeText}",
                color = InkTertiary,
                fontSize = 11.sp,
                maxLines = 1,
            )
            if (figure.summary.isNotBlank()) {
                Spacer(Modifier.height(4.dp))
                Text(
                    text = figure.summary,
                    color = InkSecondary,
                    fontSize = 12.sp,
                    lineHeight = 17.sp,
                    maxLines = 2,
                )
            }
        }
    }
}
