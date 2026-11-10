package com.historyatlas.app.ui.theme

/**
 * SCHEMA §6 的 colorKey 常量。
 *
 * 数据文件里写的是字符串字面量，这里给出对应的常量便于代码引用与拼写校验。
 * 任何不在此枚举中的键都会走 [colorFor] 的哈希回退。
 */
object ColorKeys {
    // ---- 中国史 ----
    const val STONE = "stone"
    const val CYAN = "cyan"
    const val ZHOU = "zhou"
    const val BLUE = "blue"
    const val HAN = "han"
    const val GREEN = "green"
    const val SUI_TANG = "sui-tang"
    const val YELLOW = "yellow"
    const val YUAN = "yuan"
    const val PINK = "pink"
    const val QING = "qing"
    const val GRAY = "gray"
    const val MODERN = "modern"
    const val PURPLE = "purple"

    // ---- 世界史 ----
    const val PREHISTORY = "prehistory"
    const val MESOPOTAMIA = "mesopotamia"
    const val INDIA = "india"
    const val GREECE = "greece"
    const val ROME = "rome"
    const val MEDIEVAL = "medieval"
    const val RENAISSANCE = "renaissance"
    const val EARLYMODERN = "earlymodern"
    const val CONTEMPORARY = "contemporary"

    /** 全部合法 colorKey。 */
    val ALL: List<String> = listOf(
        STONE, CYAN, ZHOU, BLUE, HAN, GREEN, SUI_TANG, YELLOW,
        YUAN, PINK, QING, GRAY, MODERN, PURPLE,
        PREHISTORY, MESOPOTAMIA, INDIA, GREECE, ROME, MEDIEVAL,
        RENAISSANCE, EARLYMODERN, CONTEMPORARY,
    )

    /** colorKey → 中文标签，用于图例与调试。 */
    val LABELS: Map<String, String> = mapOf(
        STONE to "石器/远古",
        CYAN to "夏商",
        ZHOU to "西周/东周",
        BLUE to "秦",
        HAN to "汉",
        GREEN to "三国两晋南北朝",
        SUI_TANG to "隋唐",
        YELLOW to "五代宋辽金",
        YUAN to "元",
        PINK to "明",
        QING to "清",
        GRAY to "民国/近代",
        MODERN to "现代",
        PURPLE to "跨朝代/专题",
        PREHISTORY to "史前",
        MESOPOTAMIA to "两河/埃及",
        INDIA to "印度河",
        GREECE to "古希腊",
        ROME to "古罗马",
        MEDIEVAL to "中世纪",
        RENAISSANCE to "文艺复兴",
        EARLYMODERN to "近代早期",
        CONTEMPORARY to "当代",
    )

    /** 是否为已知 colorKey。 */
    fun isKnown(key: String): Boolean = ALL.contains(key.trim().lowercase())

    /** 中文标签，未知键回退为键本身。 */
    fun label(key: String): String = LABELS[key.trim().lowercase()] ?: key
}
