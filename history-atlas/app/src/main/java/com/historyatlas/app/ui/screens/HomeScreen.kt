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
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.historyatlas.app.data.HistoryRepository
import com.historyatlas.app.ui.components.AtlasCard
import com.historyatlas.app.ui.components.SectionHeader
import com.historyatlas.app.ui.theme.CardSurface
import com.historyatlas.app.ui.theme.InkPrimary
import com.historyatlas.app.ui.theme.InkSecondary
import com.historyatlas.app.ui.theme.InkTertiary
import com.historyatlas.app.ui.theme.OutlineSoft
import com.historyatlas.app.ui.theme.Paper
import com.historyatlas.app.ui.theme.colorFor

/**
 * 首页：分支切换 + 功能入口 + 内容概览。
 */
@Composable
fun HomeScreen(
    repository: HistoryRepository,
    scope: String,
    onScopeChange: (String) -> Unit,
    onOpenTree: () -> Unit,
    onOpenAxis: () -> Unit,
    onOpenFigures: () -> Unit,
    onOpenEvents: () -> Unit,
    onOpenSearch: () -> Unit,
    onOpenCompare: () -> Unit,
) {
    // 数据在后台线程解析完成前统计为 0；解析完成后 loadState 变化触发重组刷新。
    val loadState by repository.loadState.collectAsStateWithLifecycle()
    val stats = remember(scope, loadState) { repository.statisticsPeek(scope) }
    val scopeName = if (scope == HistoryRepository.SCOPE_WORLD) "世界史" else "中国史"

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(Paper)
            // 首页没有 Scaffold 包裹，必须自己避开状态栏，
            // 否则「历史图鉴」标题会顶到手机最上沿、与时间/信号图标重叠。
            .statusBarsPadding(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(
            start = 20.dp, end = 20.dp, top = 12.dp, bottom = 20.dp,
        ),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Column {
                Text(
                    text = "历史图鉴",
                    style = MaterialTheme.typography.headlineLarge,
                    color = InkPrimary,
                    fontWeight = FontWeight.Bold,
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "看得见的年表，点得开的细节",
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkTertiary,
                )
            }
        }

        // ---- 分支切换 ----
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
                    StatCell("时期", stats.periodCount.toString())
                    StatDivider()
                    StatCell("事件", stats.eventCount.toString())
                    StatDivider()
                    StatCell("人物", stats.figureCount.toString())
                }
            }
        }

        item { SectionHeader("$scopeName 概览") }

        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                EntryCard(
                    icon = Icons.Outlined.AutoStories,
                    title = "年表总览",
                    desc = "分块年表树，一眼看清朝代更替",
                    accent = colorFor("han").block,
                    onClick = onOpenTree,
                )
                EntryCard(
                    icon = Icons.Outlined.Timeline,
                    title = "时间轴",
                    desc = "横向缩放，跨越千年纵览大事件",
                    accent = colorFor("sui-tang").block,
                    onClick = onOpenAxis,
                )
                EntryCard(
                    icon = Icons.Outlined.AccountBalance,
                    title = "人物志",
                    desc = "帝王将相、思想家、科学家与探索者",
                    accent = colorFor("greece").block,
                    onClick = onOpenFigures,
                )
                EntryCard(
                    icon = Icons.Outlined.Public,
                    title = "事件流",
                    desc = "按时间与分类浏览全部历史事件",
                    accent = colorFor("rome").block,
                    onClick = onOpenEvents,
                )
                EntryCard(
                    icon = Icons.Outlined.CompareArrows,
                    title = "中外对照",
                    desc = "中国史与世界史同期并排比对",
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
                    .background(Color(0xFFF3EFE6), RoundedCornerShape(10.dp))
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
                            "史实以通行史料为准，存疑之处从两说。",
                        color = InkTertiary,
                        fontSize = 11.sp,
                        lineHeight = 17.sp,
                    )
                }
            }
        }
    }
}

/** 分支切换分段控件。 */
@Composable
private fun ScopeSwitcher(scope: String, onScopeChange: (String) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFEDE8DE), RoundedCornerShape(10.dp))
            .padding(3.dp),
    ) {
        listOf(
            HistoryRepository.SCOPE_CHINA to "中国史",
            HistoryRepository.SCOPE_WORLD to "世界史",
        ).forEach { (key, label) ->
            val selected = scope == key
            Box(
                modifier = Modifier
                    .weight(1f)
                    .background(
                        if (selected) CardSurface else Color.Transparent,
                        RoundedCornerShape(8.dp),
                    )
                    .clickable { onScopeChange(key) }
                    .padding(vertical = 9.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = label,
                    color = if (selected) InkPrimary else InkTertiary,
                    fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
                    fontSize = 14.sp,
                )
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
            text = "搜索朝代、事件、人物…",
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
