package com.scienceatlas.app.ui.theme

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
 * 科学图鉴主题。
 *
 * - 刻意**关闭** dynamicColor：本 App 的视觉核心是分期色块的稳定配色，
 *   跟随系统壁纸变化会破坏「同一分期始终同色」的语义。
 * - 以浅色为主，深色为兜底。
 */
private val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryContainer,
    onPrimaryContainer = Color(0xFF12213F),
    secondary = Secondary,
    onSecondary = Color.White,
    secondaryContainer = SecondaryContainer,
    onSecondaryContainer = Color(0xFF10322F),
    tertiary = Color(0xFF6A5C8E),
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFE9E0F5),
    onTertiaryContainer = Color(0xFF241A3D),
    background = Paper,
    onBackground = InkPrimary,
    surface = CardSurface,
    onSurface = InkPrimary,
    surfaceVariant = Color(0xFFF0F3F8),
    onSurfaceVariant = InkSecondary,
    surfaceContainerLowest = Color.White,
    surfaceContainerLow = Color(0xFFFAFBFD),
    surfaceContainer = Color(0xFFF4F7FA),
    surfaceContainerHigh = Color(0xFFEDF1F6),
    surfaceContainerHighest = Color(0xFFE7EBF2),
    outline = Color(0xFFAFB7C4),
    outlineVariant = OutlineSoft,
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorContainer,
    onErrorContainer = Color(0xFF410E0B),
    inverseSurface = Color(0xFF2D323B),
    inverseOnSurface = Color(0xFFF2F4F8),
    inversePrimary = Color(0xFFAAC5F0),
    scrim = Color(0xFF000000),
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFAAC5F0),
    onPrimary = Color(0xFF12305C),
    primaryContainer = Color(0xFF2A4675),
    onPrimaryContainer = PrimaryContainer,
    secondary = Color(0xFF96CFC4),
    onSecondary = Color(0xFF00382F),
    secondaryContainer = Color(0xFF1C5B53),
    onSecondaryContainer = SecondaryContainer,
    tertiary = Color(0xFFC9BCDF),
    onTertiary = Color(0xFF312A47),
    background = DarkSurface,
    onBackground = DarkInk,
    surface = Color(0xFF1E2128),
    onSurface = DarkInk,
    surfaceVariant = Color(0xFF444952),
    onSurfaceVariant = Color(0xFFC6CCD6),
    outline = Color(0xFF8F96A3),
    outlineVariant = Color(0xFF3E434C),
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
 * 科学图鉴主题。
 *
 * @param darkTheme 是否使用深色配色；默认跟随系统。
 * @param content 主题内容。
 */
@Composable
fun ScienceAtlasTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors
    val extra = if (darkTheme) {
        AtlasExtraColors(
            paper = Color(0xFF14161B),
            ink = DarkInk,
            inkSecondary = Color(0xFFC2C8D2),
            inkTertiary = Color(0xFF9299A6),
            outlineSoft = Color(0xFF363A43),
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
 * 便捷入口：当前主题下分期色块的底色。
 */
@Composable
fun atlasColorFor(colorKey: String, fallbackId: String = ""): AtlasColor = colorFor(colorKey, fallbackId)
