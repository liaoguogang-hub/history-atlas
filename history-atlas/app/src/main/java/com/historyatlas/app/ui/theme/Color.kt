package com.historyatlas.app.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * 历史图鉴配色 —— 淡雅马卡龙色系。
 *
 * 设计基调：柔和粉彩底 + 深色文字，强调「长文阅读 + 色块分块」的观感。
 * 每个 colorKey 对应一组 [block]（色块底色）与 [accent]（强调色），
 * 底色用于时期色块 / 标签背景，强调色用于图标与高亮文字，
 * 保证底色浅时文字仍保持足够的对比度。
 */

// ---------------------------------------------------------------------------
// 基础色板
// ---------------------------------------------------------------------------

/** 纸面底色，接近宣纸的暖白。 */
val Paper = Color(0xFFFDFBF7)

/** 卡片底色。 */
val CardSurface = Color(0xFFFFFFFF)

/** 主要文字色（深墨褐，比纯黑柔和）。 */
val InkPrimary = Color(0xFF2E2A26)

/** 次要文字色。 */
val InkSecondary = Color(0xFF6B6259)

/**  tertiary 文字色 / 弱提示。 */
val InkTertiary = Color(0xFF9A9188)

/** 分割线。 */
val OutlineSoft = Color(0xFFE8E2D9)

/** 主色调（墨玉青，呼应历史感）。 */
val Primary = Color(0xFF3E6B6B)

/** 主色容器。 */
val PrimaryContainer = Color(0xFFDCEBEA)

/** 次色调（陈旧青铜）。 */
val Secondary = Color(0xFF8A6F4D)

/** 次色容器。 */
val SecondaryContainer = Color(0xFFF2E7D6)

/** 错误色。 */
val ErrorRed = Color(0xFFB3261E)
val ErrorContainer = Color(0xFFF9DEDC)

/** 暗色主题对应色（App 以浅色为主，暗色仅作兜底）。 */
val DarkSurface = Color(0xFF1B1917)
val DarkInk = Color(0xFFEAE2D9)

/**
 * 单个 colorKey 的配色组。
 *
 * @param block 色块底色（浅）。
 * @param accent 强调色（深一档，用于图标 / 描边 / 强调文字）。
 */
data class AtlasColor(
    val block: Color,
    val accent: Color,
)

/**
 * colorKey → 配色的完整映射，覆盖 SCHEMA §6 枚举的全部键。
 */
val AtlasColorMap: Map<String, AtlasColor> = mapOf(
    // ---- 中国史 ----
    "stone" to AtlasColor(Color(0xFFE8E2D6), Color(0xFF8A7F6B)),
    "cyan" to AtlasColor(Color(0xFFD7EBEA), Color(0xFF2F6F6E)),
    "zhou" to AtlasColor(Color(0xFFE0E7F2), Color(0xFF4A6390)),
    "blue" to AtlasColor(Color(0xFFD6E4F5), Color(0xFF3A5F9E)),
    "han" to AtlasColor(Color(0xFFE3DFF2), Color(0xFF5C4E92)),
    "green" to AtlasColor(Color(0xFFDDEBD9), Color(0xFF4C7A45)),
    "sui-tang" to AtlasColor(Color(0xFFF6E6CB), Color(0xFF9A6B2C)),
    "yellow" to AtlasColor(Color(0xFFF7EFC9), Color(0xFF8F7520)),
    "yuan" to AtlasColor(Color(0xFFE2EEDB), Color(0xFF5E7A3C)),
    "pink" to AtlasColor(Color(0xFFF7DDE2), Color(0xFFA85263)),
    "qing" to AtlasColor(Color(0xFFE8E0EF), Color(0xFF6B5585)),
    "gray" to AtlasColor(Color(0xFFE6E4E1), Color(0xFF6E6A66)),
    "modern" to AtlasColor(Color(0xFFDDE4EC), Color(0xFF4C5F75)),
    "purple" to AtlasColor(Color(0xFFEADDF1), Color(0xFF7A4C8C)),

    // ---- 世界史 ----
    "prehistory" to AtlasColor(Color(0xFFEDE6DA), Color(0xFF857862)),
    "mesopotamia" to AtlasColor(Color(0xFFF3E2C9), Color(0xFFA06F31)),
    "india" to AtlasColor(Color(0xFFF8E0C9), Color(0xFFB06A2E)),
    "greece" to AtlasColor(Color(0xFFDCE7F2), Color(0xFF3F6791)),
    "rome" to AtlasColor(Color(0xFFF0DCD8), Color(0xFF9A5148)),
    "medieval" to AtlasColor(Color(0xFFE2E1D6), Color(0xFF6D6A52)),
    "renaissance" to AtlasColor(Color(0xFFF5E0E6), Color(0xFF9C5570)),
    "earlymodern" to AtlasColor(Color(0xFFDCE8E4), Color(0xFF3F6E64)),
    "contemporary" to AtlasColor(Color(0xFFE4E8EE), Color(0xFF566175)),
)

/**
 * 未知 colorKey 的哈希回退调色板。
 *
 * 当数据里出现 SCHEMA §6 未列出的键时，按 id 哈希取这里的一组，
 * 保证任意 colorKey 都有稳定且柔和的配色。
 */
private val FallbackPalette: List<AtlasColor> = listOf(
    AtlasColor(Color(0xFFE7E3F0), Color(0xFF6B5C8E)),
    AtlasColor(Color(0xFFDFEBE0), Color(0xFF4F7A55)),
    AtlasColor(Color(0xFFF3E6D8), Color(0xFF9A7748)),
    AtlasColor(Color(0xFFDDE9F0), Color(0xFF4B7288)),
    AtlasColor(Color(0xFFF2E1E6), Color(0xFF9C5A6C)),
    AtlasColor(Color(0xFFE9EDE0), Color(0xFF6E7849)),
)

/**
 * 按 colorKey 取配色；未知键用 id 哈希回退。
 *
 * @param colorKey 数据中的 colorKey，可为空。
 * @param fallbackId 未命中时用于哈希的 id（通常是时期 id）。
 */
fun colorFor(colorKey: String, fallbackId: String = ""): AtlasColor {
    val key = colorKey.trim().lowercase()
    if (key.isNotEmpty()) {
        AtlasColorMap[key]?.let { return it }
    }
    // 哈希回退：取 id 字符和，稳定分布到回退调色板
    val source = fallbackId.ifEmpty { key }
    if (source.isEmpty()) return FallbackPalette.first()
    val hash = source.fold(0) { acc, ch -> (acc * 31 + ch.code) and 0x7FFFFFFF }
    return FallbackPalette[hash % FallbackPalette.size]
}
