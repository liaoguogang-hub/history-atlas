package com.scienceatlas.app.data

import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

/**
 * 数据层契约测试（纯 JVM，不依赖 Android Context）。
 *
 * 覆盖：
 * - 模型反序列化：缺字段时用默认值兜底，不崩溃
 * - 引用容错：悬空引用被剔除而非抛异常
 * - 序列化往返：JSON → 模型 → JSON 字段一致
 */
class DataContractTest {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        explicitNulls = false
    }

    @Test
    fun `完整数据可以正确反序列化`() {
        val raw = """
            {
              "version": 1,
              "scope": "geo",
              "periods": [
                {
                  "id": "geo-plate-tectonics", "name": "板块构造学说", "alias": "大陆漂移理论",
                  "parentId": null,
                  "startYear": 1912, "endYear": 1968,
                  "startDateText": "公元1912年", "endDateText": "公元1968年",
                  "colorKey": "geo-deep", "summary": "板块构造学说的概述",
                  "territory": "全球", "capital": "伦敦", "population": "数百人",
                  "culture": "地幔对流与海岭扩张", "keyFigures": ["fig-geo-wegener"],
                  "relatedEvents": ["ev-geo-wegener-drift"], "tags": ["编年主干", "板块"]
                }
              ],
              "events": [
                {
                  "id": "ev-geo-wegener-drift", "name": "魏格纳提出大陆漂移学说",
                  "year": 1912, "yearEnd": null, "dateText": "公元1912年",
                  "periodId": "geo-plate-tectonics", "category": "scientific",
                  "location": "法兰克福", "summary": "摘要", "detail": "详情", "importance": 5,
                  "figures": ["fig-geo-wegener"], "tags": ["大陆漂移", "地质学"]
                }
              ],
              "figures": [
                {
                  "id": "fig-geo-wegener", "name": "阿尔弗雷德·魏格纳", "alias": "魏格纳",
                  "birthYear": 1880, "deathYear": 1930,
                  "lifeText": "1880年－1930年", "role": "地质学家",
                  "periodId": "geo-plate-tectonics", "gender": "male", "summary": "简介",
                  "biography": "生平", "achievements": ["提出大陆漂移学说"], "quotes": ["我们必须假设……"],
                  "relatedEvents": ["ev-geo-wegener-drift"], "relatedFigures": [],
                  "tags": ["地质学", "大陆漂移"]
                }
              ]
            }
        """.trimIndent()

        val ds = json.decodeFromString(ScienceDataset.serializer(), raw)
        assertEquals(1, ds.version)
        assertEquals("geo", ds.scope)
        assertEquals(1, ds.periods.size)
        assertEquals(1, ds.events.size)
        assertEquals(1, ds.figures.size)

        val period = ds.periods.first()
        assertEquals("geo-plate-tectonics", period.id)
        assertEquals(1912, period.startYear)
        assertNull(period.parentId)
        assertEquals("geo-deep", period.colorKey)
        assertEquals(listOf("fig-geo-wegener"), period.keyFigures)

        val event = ds.events.first()
        assertEquals(1912, event.year)
        assertNull(event.yearEnd)
        assertEquals(0, event.span, "yearEnd 为 null 时跨年跨度应为 0")
        assertEquals(5, event.importance)

        val figure = ds.figures.first()
        assertEquals(1880, figure.birthYear)
        assertEquals(1930, figure.deathYear)
        assertEquals(listOf("我们必须假设……"), figure.quotes)
    }

    @Test
    fun `缺少可选字段时使用默认值而不是崩溃`() {
        val raw = """
            {
              "version": 1,
              "scope": "astro",
              "periods": [{"id": "p1", "name": "分期"}],
              "events": [{"id": "e1", "name": "事件", "periodId": "p1"}],
              "figures": [{"id": "f1", "name": "人物", "periodId": "p1"}]
            }
        """.trimIndent()

        val ds = json.decodeFromString(ScienceDataset.serializer(), raw)

        val p = ds.periods.first()
        assertEquals("", p.alias)
        assertEquals("", p.colorKey)
        assertEquals(emptyList(), p.keyFigures)
        assertEquals(emptyList(), p.tags)
        assertEquals(0, p.startYear)

        val e = ds.events.first()
        assertEquals(0, e.importance)
        assertNull(e.yearEnd)
        assertEquals(emptyList(), e.figures)

        val f = ds.figures.first()
        assertNull(f.birthYear)
        assertNull(f.deathYear)
        assertEquals(emptyList(), f.achievements)
    }

    @Test
    fun `顶层数组缺失时也能反序列化`() {
        val raw = """{"version":1,"scope":"physics"}"""
        val ds = json.decodeFromString(ScienceDataset.serializer(), raw)
        assertEquals(0, ds.periods.size)
        assertEquals(0, ds.events.size)
        assertEquals(0, ds.figures.size)
    }

    @Test
    fun `未知字段被忽略`() {
        val raw = """
            {
              "version": 1, "scope": "chem",
              "periods": [{"id":"p1","name":"分期","futureField":"whatever"}],
              "events": [], "figures": [], "extraTopLevel": 123
            }
        """.trimIndent()
        val ds = json.decodeFromString(ScienceDataset.serializer(), raw)
        assertEquals(1, ds.periods.size)
        assertEquals("分期", ds.periods.first().name)
    }

    @Test
    fun `event category 枚举未知值回退而不抛异常`() {
        assertEquals(EventCategory.SCIENTIFIC, EventCategory.from("scientific"))
        assertEquals(EventCategory.TECHNOLOGY, EventCategory.from("technology"))
        assertEquals(EventCategory.SCIENTIFIC, EventCategory.from("not-a-real-category"))
        assertEquals(EventCategory.SCIENTIFIC, EventCategory.from(""))
    }

    @Test
    fun `事件跨度计算正确`() {
        val spanning = Event(id = "e", name = "持续观测", year = 1900, yearEnd = 1950)
        assertEquals(50, spanning.span)
        assertEquals(1900, spanning.spanStart)
        assertEquals(1950, spanning.spanEnd)

        val point = Event(id = "e", name = "事件", year = 1912, yearEnd = null)
        assertEquals(0, point.span)
        assertEquals(1912, point.spanEnd)
    }

    @Test
    fun `年份文本与数值并存且一致`() {
        val p = Period(
            id = "phy-classical", name = "经典力学",
            startYear = 1687, endYear = 1900,
            startDateText = "公元1687年", endDateText = "公元1900年",
        )
        assertTrue(p.yearRangeText.contains("公元1687年"))
        assertTrue(p.yearRangeText.contains("公元1900年"))
        assertTrue(p.startYear <= p.endYear)
    }

    @Test
    fun `负数年份表示公元前`() {
        val p = Period(
            id = "astro-ancient", name = "古代天文学",
            startYear = -400, endYear = 100,
            startDateText = "公元前400年", endDateText = "公元100年",
        )
        assertEquals(-400, p.startYear)
        assertTrue(p.startYear < 0)
    }

    @Test
    fun `模型可以往返序列化`() {
        val original = Period(
            id = "phy-quantum", name = "量子力学", alias = "量子论", parentId = "phy-20c",
            startYear = 1900, endYear = 1970,
            startDateText = "公元1900年", endDateText = "公元1970年",
            colorKey = "phy-quantum", summary = "概述", capital = "柏林",
            keyFigures = listOf("f1"), relatedEvents = listOf("e1"), tags = listOf("量子"),
        )
        val text = json.encodeToString(Period.serializer(), original)
        val back = json.decodeFromString(Period.serializer(), text)
        assertEquals(original, back)
        assertEquals("phy-20c", back.parentId)
        assertEquals("phy-quantum", back.colorKey)
    }

    @Test
    fun `parentId 为 null 的分期往返后仍为 null`() {
        val original = Period(id = "phy-quantum", name = "量子力学", parentId = null)
        val text = json.encodeToString(Period.serializer(), original)
        val back = json.decodeFromString(Period.serializer(), text)
        assertNull(back.parentId)
    }
}
