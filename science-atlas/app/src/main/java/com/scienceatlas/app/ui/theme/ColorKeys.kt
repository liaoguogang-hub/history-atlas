package com.scienceatlas.app.ui.theme

/**
 * 配色键常量。
 *
 * 数据文件里写的是字符串字面量，这里给出对应的常量便于代码引用与拼写校验。
 * 任何不在此枚举中的键都会走 [colorFor] 的哈希回退。
 */
object ColorKeys {
    // ---- 地理 ----
    const val GEO_DEEP = "geo-deep"
    const val GEO_COAST = "geo-coast"
    const val GEO_PLAIN = "geo-plain"
    const val GEO_MOUNTAIN = "geo-mountain"
    const val GEO_DESERT = "geo-desert"
    const val GEO_POLAR = "geo-polar"
    const val GEO_RIVER = "geo-river"
    const val GEO_OCEAN = "geo-ocean"
    const val GEO_VOLCANO = "geo-volcano"
    const val GEO_KARST = "geo-karst"

    // ---- 天文 ----
    const val ASTRO_DEEP = "astro-deep"
    const val ASTRO_SOLAR = "astro-solar"
    const val ASTRO_PLANET = "astro-planet"
    const val ASTRO_COMET = "astro-comet"
    const val ASTRO_GALAXY = "astro-galaxy"
    const val ASTRO_TELESCOPE = "astro-telescope"
    const val ASTRO_QUANTA = "astro-quanta"
    const val ASTRO_COSMO = "astro-cosmo"

    // ---- 物理 ----
    const val PHY_CLASSICAL = "phy-classical"
    const val PHY_THERMO = "phy-thermo"
    const val PHY_EM = "phy-em"
    const val PHY_QUANTUM = "phy-quantum"
    const val PHY_NUCLEAR = "phy-nuclear"
    const val PHY_CONDENSED = "phy-condensed"
    const val PHY_PARTICLE = "phy-particle"
    const val PHY_RELATIVITY = "phy-relativity"
    const val PHY_WAVE = "phy-wave"
    const val PHY_ASTRO = "phy-astro"

    // ---- 化学 ----
    const val CHEM_ALCHEMY = "chem-alchemy"
    const val CHEM_ATOMIC = "chem-atomic"
    const val CHEM_PERIODIC = "chem-periodic"
    const val CHEM_ORGANIC = "chem-organic"
    const val CHEM_ELECTRO = "chem-electro"
    const val CHEM_STRUCTURE = "chem-structure"
    const val CHEM_BIO = "chem-bio"
    const val CHEM_NUCLEAR = "chem-nuclear"
    const val CHEM_MATERIAL = "chem-material"
    const val CHEM_INDUSTRY = "chem-industry"

    /** 跨尺度 / 专题分期的专用键。 */
    const val PURPLE = "purple"

    /** 全部合法 colorKey。 */
    val ALL: List<String> = listOf(
        GEO_DEEP, GEO_COAST, GEO_PLAIN, GEO_MOUNTAIN, GEO_DESERT,
        GEO_POLAR, GEO_RIVER, GEO_OCEAN, GEO_VOLCANO, GEO_KARST,
        ASTRO_DEEP, ASTRO_SOLAR, ASTRO_PLANET, ASTRO_COMET,
        ASTRO_GALAXY, ASTRO_TELESCOPE, ASTRO_QUANTA, ASTRO_COSMO,
        PHY_CLASSICAL, PHY_THERMO, PHY_EM, PHY_QUANTUM, PHY_NUCLEAR,
        PHY_CONDENSED, PHY_PARTICLE, PHY_RELATIVITY, PHY_WAVE, PHY_ASTRO,
        CHEM_ALCHEMY, CHEM_ATOMIC, CHEM_PERIODIC, CHEM_ORGANIC, CHEM_ELECTRO,
        CHEM_STRUCTURE, CHEM_BIO, CHEM_NUCLEAR, CHEM_MATERIAL, CHEM_INDUSTRY,
        PURPLE,
    )

    /** colorKey → 中文标签，用于图例与调试。 */
    val LABELS: Map<String, String> = mapOf(
        GEO_DEEP to "地质深时",
        GEO_COAST to "海岸地貌",
        GEO_PLAIN to "平原",
        GEO_MOUNTAIN to "山地",
        GEO_DESERT to "荒漠",
        GEO_POLAR to "冰冻圈",
        GEO_RIVER to "河流水系",
        GEO_OCEAN to "海洋",
        GEO_VOLCANO to "火山",
        GEO_KARST to "喀斯特",
        ASTRO_DEEP to "深空观测",
        ASTRO_SOLAR to "太阳系",
        ASTRO_PLANET to "行星",
        ASTRO_COMET to "小天体",
        ASTRO_GALAXY to "星系",
        ASTRO_TELESCOPE to "观测技术",
        ASTRO_QUANTA to "量子与辐射",
        ASTRO_COSMO to "宇宙学",
        PHY_CLASSICAL to "经典力学",
        PHY_THERMO to "热学",
        PHY_EM to "电磁学",
        PHY_QUANTUM to "量子力学",
        PHY_NUCLEAR to "核物理",
        PHY_CONDENSED to "凝聚态",
        PHY_PARTICLE to "粒子物理",
        PHY_RELATIVITY to "相对论",
        PHY_WAVE to "波动与声学",
        PHY_ASTRO to "理论物理",
        CHEM_ALCHEMY to "炼金与早期化学",
        CHEM_ATOMIC to "原子论",
        CHEM_PERIODIC to "周期律",
        CHEM_ORGANIC to "有机化学",
        CHEM_ELECTRO to "电化学",
        CHEM_STRUCTURE to "结构化学",
        CHEM_BIO to "生物化学",
        CHEM_NUCLEAR to "核化学",
        CHEM_MATERIAL to "材料化学",
        CHEM_INDUSTRY to "工业化学",
        PURPLE to "跨尺度/专题",
    )

    /** 是否为已知 colorKey。 */
    fun isKnown(key: String): Boolean = ALL.contains(key.trim().lowercase())

    /** 中文标签，未知键回退为键本身。 */
    fun label(key: String): String = LABELS[key.trim().lowercase()] ?: key
}
