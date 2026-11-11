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
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AccountBalance
import androidx.compose.material.icons.outlined.AutoStories
import androidx.compose.material.icons.outlined.CompareArrows
import androidx.compose.material.icons.outlined.Public
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Timeline
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.components.AtlasCard
import com.scienceatlas.app.ui.components.SectionHeader
import com.scienceatlas.app.ui.theme.CardSurface
import com.scienceatlas.app.ui.theme.InkPrimary
import com.scienceatlas.app.ui.theme.InkSecondary
import com.scienceatlas.app.ui.theme.InkTertiary
import com.scienceatlas.app.ui.theme.OutlineSoft
import com.scienceatlas.app.ui.theme.Paper
import com.scienceatlas.app.ui.theme.colorFor

/**
 * 学科的中文名与主色。
 *
 * 四个学科共用同一套视觉语言，但各有主色，让用户一眼分辨当前分支。
 */
data class Discipline(val scope: String, val label: String, val short: String, val colorKey: String)

/** 四个学科的展示元数据，顺序即 App 中的切换顺序。 */
val DISCIPLINES: List<Discipline> = listOf(
    Discipline(ScienceRepository.SCOPE_GEO, "地理", "地理", "geo-deep"),
    Discipline(ScienceRepository.SCOPE_ASTRO, "天文", "天文", "astro-deep"),
    Discipline(ScienceRepository.SCOPE_PHYSICS, "物理", "物理", "phy-quantum"),
    Discipline(ScienceRepository.SCOPE_CHEM, "化学", "化学", "chem-periodic"),
)

/**
 * 首页：学科切换 + 功能入口 + 内容概览。
 */
@Composable
fun HomeScreen(
    repository: ScienceRepository,
    scope: String,
    onScopeChange: (String) -> Unit,
    onOpenTree: () -> Unit,
    onOpenAxis: () -> Unit,
    onOpenFigures: () -> Unit,
    onOpenEvents: () -> Unit,
    onOpenSearch: () -> Unit,
    onOpenCompare: () -> Unit,
) {
    // 数据在后台线程解析完成前统计为 0；解析完成后触发重组刷新。
    //
    // key 用 `loadVersion` 而不是 `loadState`：
    // 四个 scope 是依次加载的，单个 loadState 只会保留最后一个 scope 的状态，
    // 首屏那个 scope 的就绪事件很可能在首次组合之前就发完了，
    // 统计数字会一直停在 0（切到别的学科反而是对的）。
    // loadVersion 每有 scope 就绪就自增，任何 scope 的就绪都能触发刷新。
    val loadState by repository.loadState.collectAsStateWithLifecycle()
    val loadVersion by repository.loadVersion.collectAsStateWithLifecycle()
    val stats = remember(scope, loadVersion) { repository.statisticsPeek(scope) }
    val current = DISCIPLINES.firstOrNull { it.scope == scope } ?: DISCIPLINES.first()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(Paper)
            // 首页没有 Scaffold 包裹，必须自己避开状态栏，
            // 否则「科学图鉴」标题会顶到手机最上沿、与时间/信号图标重叠。
            .statusBarsPadding(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(
            start = 20.dp, end = 20.dp, top = 12.dp, bottom = 20.dp,
        ),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Column {
                Text(
                    text = "科学图鉴",
                    style = MaterialTheme.typography.headlineLarge,
                    color = InkPrimary,
                    fontWeight = FontWeight.Bold,
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "地理 · 天文 · 物理 · 化学，四门科学一条时间线",
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkTertiary,
                )
            }
        }

        // ---- 学科切换 ----
        item {
            ScopeSwitcher(scope = scope, onScopeChange = onScopeChange)
        }

        // ---- 搜索入口 ----
        item {
            SearchEntry(onClick = onOpenSearch)
        }
        // ---- 内容概览 ----
        item {
            HomeCard {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    StatCell("分期", stats.periodCount.toString())
                    StatDivider()
                    StatCell("事件", stats.eventCount.toString())
                    StatDivider()
                    StatCell("人物", stats.figureCount.toString())
                }
            }
        }

        item { SectionHeader("${current.label}概览") }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                EntryCard(
                    icon = Icons.Outlined.AutoStories,
                    title = "分期总览",
                    desc = "分块年表树，一眼看清理论更替",
                    accent = colorFor(current.colorKey).block,
                    onClick = onOpenTree,
                )
                EntryCard(
                    icon = Icons.Outlined.Timeline,
                    title = "时间轴",
                    desc = "横向缩放，跨越千年纵览大发现",
                    accent = colorFor("astro-telescope").block,
                    onClick = onOpenAxis,
                )
                EntryCard(
                    icon = Icons.Outlined.AccountBalance,
                    title = "科学家志",
                    desc = "先驱、理论家、观测者与探险家",
                    accent = colorFor("phy-quantum").block,
                    onClick = onOpenFigures,
                )
                EntryCard(
                    icon = Icons.Outlined.Public,
                    title = "发现流",
                    desc = "按时间与分类浏览全部学科事件",
                    accent = colorFor("chem-organic").block,
                    onClick = onOpenEvents,
                )
                EntryCard(
                    icon = Icons.Outlined.CompareArrows,
                    title = "四科对照",
                    desc = "地理、天文、物理、化学同期并排比对",
                    accent = colorFor("purple").block,
                    onClick = onOpenCompare,
                )
            }
        }

        item { Spacer(Modifier.height(8.dp)) }

        // ---- 数据说明 ----
        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFFEFF3F8), RoundedCornerShape(10.dp))
                    .padding(14.dp),
            ) {
                Column {
                    Text(
                        text = "离线内容库",
                        color = InkSecondary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = "全部内容随应用打包，无网络权限、不收集任何信息。" +
                            "史实以通行史料与教科书为准，存疑之处从两说。",
                        color = InkTertiary,
                        fontSize = 11.sp,
                        lineHeight = 17.sp,
                    )
                }
            }
        }
    }
}

/**
 * 学科切换分段控件。
 *
 * 四个学科用两行两列排布：四列在窄屏上每个标签会被压得读不清，
 * 两行两列则每格都能放下「化学」这样的双字标签。
 */
@Composable
private fun ScopeSwitcher(scope: String, onScopeChange: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        DISCIPLINES.chunked(2).forEach { row ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFFE8EDF4), RoundedCornerShape(10.dp))
                    .padding(3.dp),
                horizontalArrangement = Arrangement.spacedBy(3.dp),
            ) {
                row.forEach { discipline ->
                    val selected = scope == discipline.scope
                    val accent = colorFor(discipline.colorKey).accent
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .background(
                                if (selected) CardSurface else Color.Transparent,
                                RoundedCornerShape(8.dp),
                            )
                            .clickable { onScopeChange(discipline.scope) }
                            .padding(vertical = 9.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = discipline.label,
                            color = if (selected) accent else InkTertiary,
                            fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
                            fontSize = 14.sp,
                        )
                    }
                }
                // 补齐最后一行缺失的格子，避免宽度不一致
                repeat(2 - row.size) {
                    Box(Modifier.weight(1f))
                }
            }
        }
    }
}

/** 搜索入口条。 */
@Composable
private fun SearchEntry(onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Outlined.Search,
            contentDescription = null,
            tint = InkTertiary,
            modifier = Modifier.size(18.dp),
        )
        Spacer(Modifier.width(10.dp))
        Text(
            text = "搜索分期、发现、科学家…",
            color = InkTertiary,
            fontSize = 14.sp,
        )
    }
}

/** 统计数字格。 */
@Composable
private fun StatCell(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            color = InkPrimary,
            fontWeight = FontWeight.Bold,
        )
        Spacer(Modifier.height(2.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = InkTertiary,
        )
    }
}

/** 统计分隔竖线。 */
@Composable
private fun StatDivider() {
    Box(
        Modifier
            .width(1.dp)
            .height(32.dp)
            .background(OutlineSoft),
    )
}

/** 功能入口卡片。 */
@Composable
private fun EntryCard(
    icon: ImageVector,
    title: String,
    desc: String,
    accent: Color,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = CardSurface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, OutlineSoft),
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                Modifier
                    .size(42.dp)
                    .background(accent, RoundedCornerShape(10.dp)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = InkPrimary.copy(alpha = 0.7f),
                    modifier = Modifier.size(21.dp),
                )
            }
            Spacer(Modifier.width(14.dp))
            Column {
                Text(
                    text = title,
                    color = InkPrimary,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 15.sp,
                )
                Spacer(Modifier.height(3.dp))
                Text(
                    text = desc,
                    color = InkTertiary,
                    fontSize = 12.sp,
                )
            }
        }
    }
}

/** 通用白卡（复用 components 中的实现，保持全局视觉一致）。 */
@Composable
internal fun HomeCard(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    AtlasCard(modifier = modifier) { content() }
}
