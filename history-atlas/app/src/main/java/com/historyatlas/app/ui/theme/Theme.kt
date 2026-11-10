package com.historyatlas.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/**
 * 历史图鉴主题。
 *
 * - 刻意**关闭** dynamicColor：本 App 的视觉核心是时期色块的稳定配色，
 *   跟随系统壁纸变化会破坏「同一朝代始终同色」的语义。
 * - 以浅色为主，深色为兜底。
 */
private val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryContainer,
    onPrimaryContainer = Color(0xFF14312F),
    secondary = Secondary,
    onSecondary = Color.White,
    secondaryContainer = SecondaryContainer,
    onSecondaryContainer = Color(0xFF3B2C16),
    tertiary = Color(0xFF6A5C8E),
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFE9E0F5),
    onTertiaryContainer = Color(0xFF241A3D),
    background = Paper,
    onBackground = InkPrimary,
    surface = CardSurface,
    onSurface = InkPrimary,
    surfaceVariant = Color(0xFFF3EEE7),
    onSurfaceVariant = InkSecondary,
    surfaceContainerLowest = Color.White,
    surfaceContainerLow = Color(0xFFFDFAF5),
    surfaceContainer = Color(0xFFF7F2EB),
    surfaceContainerHigh = Color(0xFFF1EBE3),
    surfaceContainerHighest = Color(0xFFEBE4DB),
    outline = Color(0xFFB6ADA2),
    outlineVariant = OutlineSoft,
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorContainer,
    onErrorContainer = Color(0xFF410E0B),
    inverseSurface = Color(0xFF33302C),
    inverseOnSurface = Color(0xFFF7EFE6),
    inversePrimary = Color(0xFF9CD2CF),
    scrim = Color(0xFF000000),
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF9CD2CF),
    onPrimary = Color(0xFF003733),
    primaryContainer = Color(0xFF21504E),
    onPrimaryContainer = PrimaryContainer,
    secondary = Color(0xFFD9BE94),
    onSecondary = Color(0xFF3D2E13),
    secondaryContainer = Color(0xFF574529),
    onSecondaryContainer = SecondaryContainer,
    tertiary = Color(0xFFC9BCDF),
    onTertiary = Color(0xFF312A47),
    background = DarkSurface,
    onBackground = DarkInk,
    surface = Color(0xFF221F1C),
    onSurface = DarkInk,
    surfaceVariant = Color(0xFF4B463F),
    onSurfaceVariant = Color(0xFFD0C7BC),
    outline = Color(0xFF999086),
    outlineVariant = Color(0xFF4B463F),
    error = Color(0xFFF2B8B5),
    onError = Color(0xFF601410),
    errorContainer = Color(0xFF8C1D18),
    onErrorContainer = ErrorContainer,
)

/**
 * 供 UI 层读取当前深浅模式下的「纸面 / 墨色」语义色。
 */
data class AtlasExtraColors(
    val paper: Color,
    val ink: Color,
    val inkSecondary: Color,
    val inkTertiary: Color,
    val outlineSoft: Color,
    val isDark: Boolean,
)

val LocalAtlasColors = staticCompositionLocalOf {
    AtlasExtraColors(
        paper = Paper,
        ink = InkPrimary,
        inkSecondary = InkSecondary,
        inkTertiary = InkTertiary,
        outlineSoft = OutlineSoft,
        isDark = false,
    )
}

/**
 * 历史图鉴主题。
 *
 * @param darkTheme 是否使用深色配色；默认跟随系统。
 * @param content 主题内容。
 */
@Composable
fun HistoryAtlasTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors
    val extra = if (darkTheme) {
        AtlasExtraColors(
            paper = Color(0xFF171513),
            ink = DarkInk,
            inkSecondary = Color(0xFFC5BCB1),
            inkTertiary = Color(0xFF9A9188),
            outlineSoft = Color(0xFF3A3630),
            isDark = true,
        )
    } else {
        AtlasExtraColors(
            paper = Paper,
            ink = InkPrimary,
            inkSecondary = InkSecondary,
            inkTertiary = InkTertiary,
            outlineSoft = OutlineSoft,
            isDark = false,
        )
    }

    CompositionLocalProvider(LocalAtlasColors provides extra) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = AtlasTypography,
            shapes = AtlasShapes,
            content = content,
        )
    }
}

/**
 * 便捷入口：当前主题下时期色块的底色。
 */
@Composable
fun atlasColorFor(colorKey: String, fallbackId: String = ""): AtlasColor = colorFor(colorKey, fallbackId)
