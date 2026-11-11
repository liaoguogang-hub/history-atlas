package com.scienceatlas.app.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * 科学图鉴配色 —— 清朗理性色系。
 *
 * 设计基调：冷白纸面 + 深墨文字 + 每个学科一个稳定主色。
 * 每个 colorKey 对应一组 [block]（色块底色）与 [accent]（强调色），
 * 底色用于分期色块 / 标签背景，强调色用于图标与高亮文字，
 * 保证底色浅时文字仍保持足够的对比度。
 */

// ---------------------------------------------------------------------------
// 基础色板
// ---------------------------------------------------------------------------

/** 纸面底色，接近实验记录本的冷白。 */
val Paper = Color(0xFFFAFBFD)

/** 卡片底色。 */
val CardSurface = Color(0xFFFFFFFF)

/** 主要文字色（深墨蓝灰，比纯黑柔和）。 */
val InkPrimary = Color(0xFF252A33)

/** 次要文字色。 */
val InkSecondary = Color(0xFF5C6472)

/** tertiary 文字色 / 弱提示。 */
val InkTertiary = Color(0xFF939BA9)

/** 分割线。 */
val OutlineSoft = Color(0xFFE4E8EF)

/** 主色调（深空蓝，呼应科学感）。 */
val Primary = Color(0xFF33518C)

/** 主色容器。 */
val PrimaryContainer = Color(0xFFDDE5F5)

/** 次色调（青碧，呼应观测仪器）。 */
val Secondary = Color(0xFF2E7D74)

/** 次色容器。 */
val SecondaryContainer = Color(0xFFD7EDE9)

/** 错误色。 */
val ErrorRed = Color(0xFFB3261E)
val ErrorContainer = Color(0xFFF9DEDC)

/** 暗色主题对应色（App 以浅色为主，暗色仅作兜底）。 */
val DarkSurface = Color(0xFF171A20)
val DarkInk = Color(0xFFE6EAF2)

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
 * colorKey → 配色的完整映射。
 *
 * 四个学科各有自己的主色系：
 * - 地理：青绿 → 大地与海洋
 * - 天文：靛蓝 → 深空
 * - 物理：紫罗兰 → 抽象与精妙
 * - 化学：琥珀 → 反应与物质
 */
val AtlasColorMap: Map<String, AtlasColor> = mapOf(
    // ---- 地理 ----
    "geo-deep" to AtlasColor(Color(0xFFD9EAE4), Color(0xFF2F6B5E)),
    "geo-coast" to AtlasColor(Color(0xFFDCEAF3), Color(0xFF356A8C)),
    "geo-plain" to AtlasColor(Color(0xFFE7EFD8), Color(0xFF557A3C)),
    "geo-mountain" to AtlasColor(Color(0xFFE3E4EC), Color(0xFF525A70)),
    "geo-desert" to AtlasColor(Color(0xFFF6E8D2), Color(0xFF8F6A28)),
    "geo-polar" to AtlasColor(Color(0xFFE2ECF4), Color(0xFF3F6E8C)),
    "geo-river" to AtlasColor(Color(0xFFD7EAEC), Color(0xFF2E6E72)),
    "geo-ocean" to AtlasColor(Color(0xFFD5E4F2), Color(0xFF2F5E90)),
    "geo-volcano" to AtlasColor(Color(0xFFF5DED6), Color(0xFFA4523C)),
    "geo-karst" to AtlasColor(Color(0xFFE4E7DC), Color(0xFF5C6544)),

    // ---- 天文 ----
    "astro-deep" to AtlasColor(Color(0xFFDFE3F3), Color(0xFF3A4684)),
    "astro-solar" to AtlasColor(Color(0xFFFAE7C9), Color(0xFF9A6C1E)),
    "astro-planet" to AtlasColor(Color(0xFFDCE7F2), Color(0xFF3F6791)),
    "astro-comet" to AtlasColor(Color(0xFFDEE9F5), Color(0xFF38659A)),
    "astro-galaxy" to AtlasColor(Color(0xFFE8DFF0), Color(0xFF6C4E8C)),
    "astro-telescope" to AtlasColor(Color(0xFFD9E6EC), Color(0xFF33657A)),
    "astro-quanta" to AtlasColor(Color(0xFFEDE0F2), Color(0xFF7A4C90)),
    "astro-cosmo" to AtlasColor(Color(0xFFE4E1F2), Color(0xFF58549A)),

    // ---- 物理 ----
    "phy-classical" to AtlasColor(Color(0xFFE7E4F3), Color(0xFF5C5590)),
    "phy-thermo" to AtlasColor(Color(0xFFF7E0D8), Color(0xFFA25744)),
    "phy-em" to AtlasColor(Color(0xFFD8E7F0), Color(0xFF2F6A8C)),
    "phy-quantum" to AtlasColor(Color(0xFFE5DCF2), Color(0xFF6B4A92)),
    "phy-nuclear" to AtlasColor(Color(0xFFF3E3D2), Color(0xFF8E5E2A)),
    "phy-condensed" to AtlasColor(Color(0xFFD9EAE8), Color(0xFF2C6E6A)),
    "phy-particle" to AtlasColor(Color(0xFFEADCF0), Color(0xFF774E8E)),
    "phy-relativity" to AtlasColor(Color(0xFFE0E2F0), Color(0xFF4A5090)),
    "phy-wave" to AtlasColor(Color(0xFFD6EAEF), Color(0xFF2C6B77)),
    "phy-astro" to AtlasColor(Color(0xFFE6E0F1), Color(0xFF65508F)),

    // ---- 化学 ----
    "chem-alchemy" to AtlasColor(Color(0xFFE8DFD2), Color(0xFF7A6446)),
    "chem-atomic" to AtlasColor(Color(0xFFE0E8EE), Color(0xFF41637A)),
    "chem-periodic" to AtlasColor(Color(0xFFF7E3D0), Color(0xFF96602A)),
    "chem-organic" to AtlasColor(Color(0xFFDFEBDF), Color(0xFF427A4A)),
    "chem-electro" to AtlasColor(Color(0xFFE2E0F2), Color(0xFF5A55A0)),
    "chem-structure" to AtlasColor(Color(0xFFDDE8F2), Color(0xFF37638C)),
    "chem-bio" to AtlasColor(Color(0xFFE6EFE0), Color(0xFF54763C)),
    "chem-nuclear" to AtlasColor(Color(0xFFF2DDD8), Color(0xFF9B5148)),
    "chem-material" to AtlasColor(Color(0xFFD9E9EE), Color(0xFF2E6A78)),
    "chem-industry" to AtlasColor(Color(0xFFE9E3D8), Color(0xFF6E6448)),
)

/**
 * 未知 colorKey 的哈希回退调色板。
 *
 * 当数据里出现未列出的键时，按 id 哈希取这里的一组，
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
 * @param fallbackId 未命中时用于哈希的 id（通常是分期 id）。
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
